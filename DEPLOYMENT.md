# 📦 Deployment Guide

## 🚀 Quick Deploy to PythonAnywhere (Recommended - Free Forever)

### Step 1: Sign Up
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create a free account (no credit card needed)

### Step 2: Upload Code
**Option A: From GitHub (Recommended)**
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/Fit-Check-Mirror.git
cd Fit-Check-Mirror
```

**Option B: Upload Files**
- Use the Files tab to upload your project folder

### Step 3: Install Dependencies
```bash
# In PythonAnywhere Bash console
pip3.11 install --user -r requirements.txt
```

### Step 4: Configure Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Flask**
4. Python version: **3.11**
5. Path to Flask app: `/home/yourusername/Fit-Check-Mirror/app.py`

### Step 5: Set Environment Variables
1. In the Web tab, scroll to **Environment variables**
2. Add:
   - Name: `GROQ_API_KEY`
   - Value: `your_groq_api_key_here`

### Step 6: Configure WSGI
Edit the WSGI configuration file (link in Web tab):

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/Fit-Check-Mirror'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import your Flask app
from app import app as application
```

### Step 7: Reload
Click the **Reload** button in the Web tab

### Step 8: Access Your App
Your app will be live at: `https://yourusername.pythonanywhere.com`

---

## 🚂 Alternative: Deploy to Railway

### Prerequisites
- GitHub account
- Railway account ([railway.app](https://railway.app))

### Steps
1. Push your code to GitHub
2. Go to Railway dashboard
3. Click **New Project** → **Deploy from GitHub**
4. Select your repository
5. Add environment variable:
   - `GROQ_API_KEY`: your_key_here
6. Railway auto-detects Flask and deploys!

**Note:** Railway free tier gives $5/month credit

---

## ✈️ Alternative: Deploy to Fly.io

### Prerequisites
- Install Fly CLI: `curl -L https://fly.io/install.sh | sh`

### Steps
```bash
# Login
flyctl auth login

# Launch app
flyctl launch

# Set environment variable
flyctl secrets set GROQ_API_KEY=your_key_here

# Deploy
flyctl deploy
```

---

## 🔧 Environment Variables

All platforms require:

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | `gsk_...` |

Get your Groq API key: [console.groq.com](https://console.groq.com)

---

## 📊 Platform Comparison

| Platform | Cost | Always On? | Ease | Best For |
|----------|------|------------|------|----------|
| **PythonAnywhere** | Free forever | ✅ Yes | ⭐⭐⭐⭐⭐ | Personal projects |
| **Railway** | $5 credit/mo | ✅ Yes | ⭐⭐⭐⭐ | Testing/dev |
| **Fly.io** | Free tier | ✅ Yes | ⭐⭐⭐ | Production apps |
| **Render** | Free | ❌ Sleeps | ⭐⭐⭐⭐ | Not recommended |

---

## 🐛 Troubleshooting

### App not loading?
- Check if environment variables are set correctly
- Verify GROQ_API_KEY is valid
- Check error logs in platform dashboard

### Static files not loading?
- Ensure `static/` folder is uploaded
- Check file paths are correct
- Clear browser cache

### API errors?
- Verify Groq API key is active
- Check API quota/limits
- Review error messages in logs

---

## 📞 Need Help?

- Check platform documentation
- Review error logs
- Open an issue on GitHub
