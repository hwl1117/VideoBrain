<p align="center">
  <img src="videobrain.ico" width="100" alt="VideoBrain Logo">
</p>

<h1 align="center">VideoBrain</h1>
<h3 align="center">AI-Powered Short Video Knowledge Base</h3>

<p align="center">
  <a href="https://video-brain.vercel.app">🌐 Live Demo</a> •
  <a href="https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0">💻 Download App</a> •
  <a href="#-quick-start">🚀 Quick Start</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Electron-20-blue?logo=electron" alt="Electron">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
</p>

---

## 📖 About

**VideoBrain** is an intelligent knowledge base system for short videos. Paste any short video URL, and the AI automatically extracts content, transcribes speech, performs deep analysis, and generates structured knowledge stored in a private knowledge base.

## ✨ Key Features

- 🎬 **Multi-Platform Support** — Douyin, Bilibili, YouTube, Kuaishou, TikTok, Xiaohongshu, WeChat Video
- 🧠 **AI-Powered** — Whisper speech-to-text + GPT-4 content understanding
- 🔍 **Semantic Search** — Vector database powered intelligent search
- 📚 **Knowledge Management** — Structured storage with categories and tags
- 💻 **Desktop App** — Electron desktop version, runs locally
- 🆓 **Free Option** — Local Whisper model support, no payment required

## 🏗️ Architecture

```
User pastes video URL (Frontend - Next.js)
         ↓
    Parse URL → Identify Platform
         ↓
    Download Video (yt-dlp)
         ↓
    Speech to Text (Whisper)
         ↓
    AI Deep Analysis (GPT-4)
         ↓
    Store Knowledge (ChromaDB)
         ↓
    Display Results (Frontend)
```

## 🚀 Quick Start

### Option 1: Online

Visit **https://video-brain.vercel.app**

### Option 2: Download Desktop App

1. Go to [Releases](https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0)
2. Download `VideoBrain-v2.6.0-Windows-x64.zip`
3. Extract and run `electron/electron.exe`

### Option 3: Local Development

```bash
# Clone the project
git clone https://github.com/hwl1117/VideoBrain.git
cd VideoBrain

# Quick start (Windows)
Double-click start-local.bat

# Or start manually
# Terminal 1: Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
VideoBrain/
├── backend/              # Python Backend
│   ├── api/              # FastAPI Routes
│   ├── services/         # Core Services
│   │   ├── video_downloader.py   # Video Download
│   │   ├── audio_extractor.py    # Audio Extraction
│   │   ├── speech_to_text.py     # Speech to Text
│   │   ├── visual_analyzer.py    # Visual Analysis
│   │   ├── ai_summarizer.py      # AI Summarization
│   │   └── knowledge_base.py     # Knowledge Base
│   └── requirements.txt
├── frontend/             # Next.js Frontend
│   ├── src/app/          # Page Components
│   └── package.json
├── electron/             # Electron Desktop App
│   ├── main.js           # Main Process
│   └── bin/              # Electron Runtime
├── vercel.json           # Vercel Deployment Config
└── start-local.bat       # Local Start Script
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI + SQLAlchemy |
| AI | Whisper (Speech) + GPT-4 (Analysis) |
| Database | SQLite + ChromaDB (Vector) |
| Desktop | Electron |
| Deploy | Vercel (Web) + GitHub Releases (App) |

## 🔌 API Endpoints

```http
# Process Video
POST /api/videos/process
{ "url": "https://www.douyin.com/video/xxx", "language": "zh" }

# Search Knowledge
POST /api/knowledge/search
{ "query": "artificial intelligence", "limit": 10 }

# Get Video Info
GET /api/videos/{video_id}

# Health Check
GET /health
```

## 🎯 Processing Pipeline

```
1. Parse URL → Identify platform and video ID
       ↓
2. Download Video → Get video file
       ↓
3. Extract Audio → Separate audio/video tracks
       ↓
4. Speech to Text → Whisper transcription
       ↓
5. Visual Analysis → GPT-4V key frame analysis
       ↓
6. AI Summary → Generate structured knowledge
       ↓
7. Store to DB → Vector database storage
```

## 📦 Deployment

### Web (Vercel)

Frontend is deployed to Vercel: **https://video-brain.vercel.app**

Auto-deploys on push to `master` branch.

### Desktop App (GitHub Releases)

Download: [v2.6.0 Release](https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0)

| File | Size | Description |
|------|------|-------------|
| VideoBrain-v2.6.0-Windows-x64.zip | ~134MB | Windows portable app |

## ⚙️ Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./videobrain.db

# Server
HOST=0.0.0.0
PORT=8000

# Use local Whisper (free, no API key needed)
USE_LOCAL_WHISPER=true

# Optional: OpenAI API (for GPT-4 analysis)
# OPENAI_API_KEY=your-api-key-here
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Credits

- [OpenAI](https://openai.com/) — GPT-4 & Whisper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Video Download
- [ChromaDB](https://www.trychroma.com/) — Vector Database
- [FastAPI](https://fastapi.tiangolo.com/) — Web Framework
- [Next.js](https://nextjs.org/) — React Framework
- [Electron](https://www.electronjs.org/) — Desktop Framework

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/hwl1117">hwl1117</a>
</p>
