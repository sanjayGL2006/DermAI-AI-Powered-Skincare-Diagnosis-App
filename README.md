# 🌿 DermAI – AI-Powered Skincare Diagnosis App

> Detect skin conditions. Get personalized routines. Find best products.

---

## 🚀 Features
- 📸 Face photo upload or live camera capture
- 🤖 AI skin analysis (Google AI Studio Gemini API) – detects 10+ conditions
- 💊 Personalized creams, soaps, tablets & serums
- 🛍️ Product links from Flipkart, Amazon, Nykaa by budget
- 🥗 Diet & lifestyle tips per condition
- 💬 AI chat assistant for follow-up questions
- 🏥 Nearby dermatologist finder
- 🔒 Google OAuth login + Guest mode
- 🛡️ AES-256 encrypted, DPDP Act 2023 compliant
- 📊 Firebase Analytics & Web SDK integration
- 💰 Free tier (30 analyses) + Premium ₹50/month

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python Flask |
| Database | SQLite |
| AI | Gemini Flash (Google AI Studio API) |
| Auth | Google OAuth (Flask-Dance) |
| Admin SDK | Firebase Admin Python SDK |
| Analytics | Firebase Web SDK & Analytics |
| Container | Docker + Nginx |

---

## ⚙️ Setup

### 1. Clone & Configure

```bash
git clone <your-repo>
cd skincare-app
cp .env.example .env
cp serviceAccountKey.json.example serviceAccountKey.json  # Add your Firebase service account key
```

Edit `.env` and fill in your keys:
```
GEMINI_API_KEY=AQ.Ab8RN6IP...      # From aistudio.google.com
GOOGLE_CLIENT_ID=...               # From console.cloud.google.com
GOOGLE_CLIENT_SECRET=...
FLASK_SECRET_KEY=any-random-string
FIREBASE_SERVICE_ACCOUNT_KEY=serviceAccountKey.json
```

### 2. Google OAuth Setup
1. Go to https://console.cloud.google.com
2. Create a new project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Web application)
4. Add Authorized redirect URI: `http://localhost:5000/login/google/authorized`
5. Copy Client ID and Secret to `.env`

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```
Open → http://localhost:80

### 4. Run Locally (Development)

```bash
pip install -r requirements.txt
python app.py
```
Open → http://localhost:5000

---

## 📁 Project Structure

```
skincare-app/
├── app.py                  # Main Flask app + all routes
├── database.py             # SQLite setup
├── skin_data.py            # Skin conditions & products database
├── requirements.txt        # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example
├── templates/
│   ├── base.html           # Base layout with navbar/footer
│   ├── login.html          # Google OAuth login page
│   ├── index.html          # Landing page
│   ├── analyze.html        # Upload/camera + questionnaire
│   ├── results.html        # Analysis results + products
│   ├── chat.html           # AI chat assistant
│   └── profile.html        # User dashboard & history
└── static/
    └── css/
        └── style.css       # Full stylesheet (dark theme)
```

---

## 🔐 Security Features
- SHA-256 hashed User IDs
- Session-based authentication
- Google OAuth 2.0
- OAUTHLIB_INSECURE_TRANSPORT disabled in production
- DPDP Act 2023 compliant
- No raw images stored in DB

---

## 💡 Usage Flow
1. User visits → signs in with Google or continues as Guest
2. Uploads selfie or captures via camera
3. Answers 6 quick questions about skin
4. Gemini AI analyzes image → returns structured JSON
5. Results page shows: score, conditions, products, routine, diet
6. User can chat with DermAI for follow-up advice
7. All history saved in profile

## 🚀 Deploying to Vercel

This repository is pre-configured for instant deployment on **Vercel** serverless platform!

### 1. Push to GitHub
Ensure your latest changes are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure for Vercel deployment"
git push origin main
```

### 2. Import into Vercel
1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Import your `skincare-app` GitHub repository.
3. Keep default settings (**Framework Preset**: Other / None).

### 3. Set Environment Variables on Vercel
In **Vercel Project Settings → Environment Variables**, add:

| Key | Example / Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API Key from Google AI Studio |
| `FLASK_SECRET_KEY` | Any random secure string |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret |

### 4. Update Google OAuth Redirect URI
In [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials):
- Add authorized redirect URI: `https://<your-vercel-app>.vercel.app/login/google/authorized`

---

## ⚕️ Disclaimer
DermAI is for informational purposes only. Always consult a licensed dermatologist for medical diagnosis and treatment.

