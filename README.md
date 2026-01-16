# 🪞 Fit Check Mirror

An AI-powered outfit analyzer that rates your drip and provides honest fashion feedback! Upload a photo or use your camera to get instant style ratings, roasts, and improvement tips.

<!-- Last Updated (Force Refresh): 2026-01-16 -->

## ✨ Features

- 📸 **Camera & Upload Support** - Use your webcam or upload photos
- 🎯 **AI-Powered Analysis** - Powered by Groq's Llama Vision model
- 💯 **Drip Score** - Get rated 0-100 on your outfit
- 🔥 **Honest Roasts** - Brutally honest AI feedback on your style
- 💡 **Style Tips** - Personalized improvement suggestions
- 🎨 **Multiple Categories** - Casual, Formal, Party, Street, Traditional, Sports
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎤 **Text-to-Speech** - Hear your roast out loud
- 📥 **Share Cards** - Download and share your drip score

## 🚀 Demo

[Live Demo](#) *(Add your deployment link here)*

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **AI Model:** Groq Llama 3.2 90B Vision
- **Text-to-Speech:** Groq Whisper Large V3 Turbo
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Comic/Sticky Note aesthetic

## 📋 Prerequisites

- Python 3.11+
- Groq API Key ([Get one here](https://console.groq.com))

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Fit-Check-Mirror
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
Fit-Check-Mirror/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version
├── Procfile              # Deployment config
├── .env                  # Environment variables (not in git)
├── .env.example          # Example env file
├── static/
│   ├── background_image.jpg
│   ├── mirror_image.png
│   ├── mobile_background.jpeg
│   ├── mobile.css        # Mobile styles
│   └── share.js          # Share card generation
└── templates/
    └── index.html        # Main UI
```

## 🎨 Outfit Categories

- 🧢 **Daily Edit** - Casual everyday wear
- 💼 **Boardroom** - Formal/office attire
- 🥂 **Evening Edit** - Party/night out outfits
- 🛹 **Urban Pulse** - Street style
- 👘 **Heritage** - Traditional wear
- 🏃 **In Motion** - Sportswear/athletic

## 🌐 Deployment

### Option 1: PythonAnywhere (Recommended - Free Forever)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code or clone from GitHub
3. Create a new web app (Flask)
4. Set environment variables in the Web tab
5. Reload your web app

### Option 2: Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project from GitHub
4. Add `GROQ_API_KEY` environment variable
5. Deploy!

### Option 3: Fly.io

```bash
flyctl launch
flyctl secrets set GROQ_API_KEY=your_key_here
flyctl deploy
```

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |

## 🎯 Usage

1. **Select Category** - Choose your outfit type
2. **Upload or Camera** - Take a photo or upload one
3. **Scan Outfit** - Let AI analyze your drip
4. **Get Roasted** - Receive your score and feedback
5. **Share** - Download your drip card

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com) AI models
- Comic-style UI inspired by sticky notes and hand-drawn aesthetics

## 📧 Contact

Created by [Your Name] - feel free to reach out!

---

⭐ Star this repo if you like it!
