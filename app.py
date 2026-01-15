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

# Configure Groq API
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

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
    return render_template('index.html')

@app.route('/roast', methods=['POST'])
def roast():
    if not GROQ_API_KEY:
         return jsonify({"status": "error", "message": "GROQ_API_KEY not set"}), 500

    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

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
            "score": roast_data.get('score', 0),
            "roast": roast_text,
            "emoji": roast_data.get('emoji', ''),
            "tips": roast_data.get('tips', 'No tips today.'),
            "audio": audio_base64
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
