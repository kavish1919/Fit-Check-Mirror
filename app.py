import os
import json
import asyncio
import base64
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
import edge_tts
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

import firebase_admin
from firebase_admin import credentials, firestore, auth

# Configure Groq API
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# Initialize Firebase
# Priority: 1. Environment Variables (for cloud), 2. JSON file (for local)
db = None

firebase_project_id = os.environ.get('FIREBASE_PROJECT_ID')
firebase_private_key = os.environ.get('FIREBASE_PRIVATE_KEY')
firebase_client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')

if firebase_project_id and firebase_private_key and firebase_client_email:
    # Cloud deployment: Use environment variables
    cred_dict = {
        "type": "service_account",
        "project_id": firebase_project_id,
        "private_key": firebase_private_key.replace('\\n', '\n'),  # Handle escaped newlines
        "client_email": firebase_client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized from environment variables!")
elif os.path.exists("firebase_credentials.json"):
    # Local development: Use JSON file
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized from credentials file!")
else:
    print("⚠️ WARNING: No Firebase credentials found. Database features will be disabled.")

# Helper: Encode Image to Base64
def encode_image(file_storage):
    return base64.b64encode(file_storage.read()).decode('utf-8')

def get_roast_from_groq(base64_image, category="General"):
    prompt = (
        f"You are a Gen Z fashion critic. The user is going for a '{category}' vibe.\n"
        "1. Assign a 'Drip Score' (0-100) based on how well they fit the '" + category + "' aesthetic.\n"
        "2. If Score < 60: ROAST IT. Be savage.\n"
        "3. If Score >= 60: HYPE IT. Be enthusiastic.\n"
        "4. Provide a string of 3-5 relevant emojis.\n"
        "5. Give 1 sentence of constructive advice specific to the '" + category + "' style (field: 'tips').\n"
        "Write exactly 2 sentences for the main text.\n"
        "Output strict JSON: {\"score\": 85, \"text\": \"Your commentary.\", \"emoji\": \"🔥\", \"tips\": \"Advice.\"}"
    )

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"ERROR: {str(e)}"

async def generate_audio(text, output_file):
    """Generates audio using edge-tts."""
    communicate = edge_tts.Communicate(text, "en-US-AnaNeural")
    await communicate.save(output_file)

@app.route('/')
def index():
    firebase_config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY', ''),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.environ.get('FIREBASE_APP_ID', '')
    }
    return render_template('index.html', firebase_config=firebase_config)

# --- Firebase Auth & User Routes ---

@app.route('/api/login', methods=['POST'])
def api_login():
    if not db: return jsonify({"error": "Database not configured"}), 503
    
    data = request.json
    id_token = data.get('idToken')
    
    try:
        # Verify the token sent from the client
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token['email']
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        # Check if user exists
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # Create new user
            user_data = {
                'email': email,
                'displayName': name,
                'photoURL': picture,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'username': None, # Must be set later
                'stats': {
                    'totalScans': 0,
                    'highestScore': 0,
                    'lowestScore': 100,
                    'averageScore': 0,
                    'totalScoreSum': 0
                }
            }
            user_ref.set(user_data)
            return jsonify({"status": "new_user", "uid": uid})
        else:
            # Update basics (in case photo changed)
            # Update basics
            user_ref.update({
                'displayName': name, 
                'photoURL': picture,
                'lastLogin': firestore.SERVER_TIMESTAMP
            })
            existing_data = user_doc.to_dict()
            username = existing_data.get('username')

            # SELF-HEALING: If username is missing in profile, check if they own one in 'usernames'
            if not username:
                try:
                    # Query usernames collection where uid == current uid
                    query = db.collection('usernames').where('uid', '==', uid).limit(1).stream()
                    for doc in query:
                        found_username = doc.id
                        print(f"🔧 Self-healing: Found orphaned username '{found_username}' for uid {uid}")
                        
                        # Fix the user profile
                        user_ref.update({'username': found_username})
                        username = found_username
                        break
                except Exception as e:
                    print(f"Self-heal error: {e}")

            return jsonify({
                "status": "existing_user", 
                "uid": uid,
                "username": username
            })
            
    except Exception as e:
        print(f"Auth Error: {e}")
        return jsonify({"error": str(e)}), 401

@app.route('/api/check-username', methods=['POST'])
def check_username():
    if not db: return jsonify({"error": "Database not configured"}), 503
    username = request.json.get('username', '').lower().strip()
    
    # Check reserved words or length
    if len(username) < 3 or len(username) > 20:
        return jsonify({"available": False, "message": "Length must be 3-20 chars"})
        
    doc = db.collection('usernames').document(username).get()
    if doc.exists:
        return jsonify({"available": False, "message": "Username taken"})
    return jsonify({"available": True, "message": "Username available!"})

@app.route('/api/set-username', methods=['POST'])
def set_username():
    if not db: return jsonify({"error": "Database not configured"}), 503
    data = request.json
    id_token = data.get('idToken')
    desired_username = data.get('username', '').lower().strip()
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Double check availability (or ownership)
        username_ref = db.collection('usernames').document(desired_username)
        username_doc = username_ref.get()
        
        if username_doc.exists:
            # Check if it belongs to THIS user (reclaiming/fixing inconsistency)
            existing_uid = username_doc.to_dict().get('uid')
            if existing_uid != uid:
                return jsonify({"error": "Username taken"}), 400
            # If uid matches, we proceed to update (re-link)
            
        # Transaction to claim username
        # (Simplified for now without full ACID transaction for brevity, 
        # normally use db.transaction() for this)
        username_ref.set({'uid': uid})
        
        db.collection('users').document(uid).update({'username': desired_username})
        
        return jsonify({"status": "success", "username": desired_username})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if not db: return jsonify({"error": "Database not configured"}), 503
    data = request.json
    id_token = data.get('idToken')
    new_name = data.get('displayName', '').strip()
    new_username = data.get('username', '').strip().lower()

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists: return jsonify({"error": "User not found"}), 404
        
        current_data = user_doc.to_dict()
        old_username = current_data.get('username')
        
        updates = {}
        if new_name:
            updates['displayName'] = new_name
            
        # Username Update Logic
        if new_username and new_username != old_username:
            # Check validity
            if len(new_username) < 3 or len(new_username) > 20: 
                return jsonify({"error": "Username must be 3-20 chars"}), 400

            # Check availability
            new_username_ref = db.collection('usernames').document(new_username)
            if new_username_ref.get().exists:
                return jsonify({"error": "Username taken"}), 400
                
            # Claim new, release old
            batch = db.batch()
            batch.set(new_username_ref, {'uid': uid})
            if old_username:
                batch.delete(db.collection('usernames').document(old_username))
            
            updates['username'] = new_username
            batch.update(user_ref, updates)
            batch.commit()
        elif updates:
            # Just updating name
            user_ref.update(updates)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Update Error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    if not db: return jsonify({"error": "Database not configured"}), 503
    data = request.json
    id_token = data.get('idToken')
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            username = user_doc.to_dict().get('username')
            batch = db.batch()
            batch.delete(user_ref)
            if username:
                batch.delete(db.collection('usernames').document(username))
            batch.commit()
            
        # Delete from Auth (Optional, requires Admin SDK)
        try:
            auth.delete_user(uid)
        except:
            pass # Client side will also sign out
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/u/<username>')
def public_profile(username):
    if not db: return "Database not configured", 503
    username = username.lower().strip()
    
    # 1. Look up UID from username
    u_doc = db.collection('usernames').document(username).get()
    if not u_doc.exists:
        return render_template('404.html', message="User not found"), 404
        
    target_uid = u_doc.to_dict()['uid']
    
    # 2. Get User Data
    user_data = db.collection('users').document(target_uid).get().to_dict()
    user_data['uid'] = target_uid # M V P: Inject UID so template has it
    
    firebase_config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY', ''),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.environ.get('FIREBASE_APP_ID', '')
    }
    
    return render_template('profile.html', user=user_data, firebase_config=firebase_config)

    # ... (existing imports and code)

def update_user_stats(uid, score):
    """Updates user stats in Firestore after a scan."""
    if not db: return
    
    user_ref = db.collection('users').document(uid)
    
    # Use a transaction or simple get/update (simple for now)
    doc = user_ref.get()
    if not doc.exists: return
    
    data = doc.to_dict()
    stats = data.get('stats', {
        'totalScans': 0, 'highestScore': 0, 'lowestScore': 100, 'averageScore': 0, 'totalScoreSum': 0
    })
    
    # Calculate new stats
    new_total_scans = stats.get('totalScans', 0) + 1
    new_total_sum = stats.get('totalScoreSum', 0) + score
    new_avg = round(new_total_sum / new_total_scans, 1)
    
    updates = {
        'stats.totalScans': new_total_scans,
        'stats.totalScoreSum': new_total_sum,
        'stats.averageScore': new_avg
    }
    
    if score > stats.get('highestScore', 0):
        updates['stats.highestScore'] = score
        
    if score < stats.get('lowestScore', 100):
        updates['stats.lowestScore'] = score
        
    user_ref.update(updates)

@app.route('/roast', methods=['POST'])
def roast():
    if not GROQ_API_KEY:
         return jsonify({"status": "error", "message": "GROQ_API_KEY not set"}), 500

    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
        
    # Check for Auth Token (Optional)
    auth_header = request.headers.get('Authorization')
    uid = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
        try:
            decoded = auth.verify_id_token(token)
            uid = decoded['uid']
        except Exception:
            pass # Ignore invalid tokens, just don't save stats

    category = request.form.get('category', 'General')

    try:
        # Encode Image
        base64_img = encode_image(file)
        
        # Call Groq
        response_text = get_roast_from_groq(base64_img, category)
        
        if not response_text:
             return jsonify({"status": "error", "message": "Failed to generate roast from Groq (Unknown Error)"}), 500
        
        if response_text.startswith("ERROR:"):
             return jsonify({"status": "error", "message": response_text}), 500

        # Parse Groq Response
        try:
            roast_data = json.loads(response_text)
        except json.JSONDecodeError:
            print("JSON Parse Error. Raw: ", response_text)
            roast_data = {"score": 0, "text": "The AI is speechless. (Error parsing response)"}

        roast_text = roast_data.get('text', 'No roast generated.')
        score = roast_data.get('score', 0)
        
        # Update User Stats if Logged In
        # Update User Stats if Logged In
        # DISABLED: Auto-save removed per user request. Use /api/save-score.
        # if uid:
        #     try:
        #         update_user_stats(uid, score)
        #         print(f"Stats updated for user {uid}")
        #     except Exception as e:
        #         print(f"Failed to update stats: {e}")
        
        # Generate Audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_filename = temp_audio.name
        
        try:
            asyncio.run(generate_audio(roast_text, temp_filename))
            
            # Read Audio and Encode to Base64
            with open(temp_filename, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        return jsonify({
            "status": "success",
            "score": score,
            "roast": roast_text,
            "emoji": roast_data.get('emoji', ''),
            "tips": roast_data.get('tips', 'No tips today.'),
            "audio": audio_base64
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/save-score', methods=['POST'])
def save_score():
    if not db: return jsonify({"error": "Database not configured"}), 503
    data = request.json
    id_token = data.get('idToken')
    score = data.get('score')
    
    if score is None:
        return jsonify({"error": "No score provided"}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        update_user_stats(uid, int(score))
        
        return jsonify({"status": "success", "saved_score": score})
    except Exception as e:
        print(f"Save Score Error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
