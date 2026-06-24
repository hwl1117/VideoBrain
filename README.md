<p align="center">
  <img src="videobrain.ico" width="100" alt="VideoBrain Logo">
</p>

<h1 align="center">VideoBrain</h1>
<h3 align="center">短视频智能知识库 | Short Video Knowledge Base</h3>

<p align="center">
  <a href="https://video-brain.vercel.app">🌐 Live Demo</a> •
  <a href="https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0">💻 Download App</a> •
  <a href="#-快速开始-quick-start">🚀 Quick Start</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Electron-20-blue?logo=electron" alt="Electron">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
</p>

---

## 🇨🇳 中文介绍

### 📖 项目简介

**VideoBrain** 是一款短视频智能知识库系统。粘贴任意短视频链接，AI 自动提取视频内容、语音转文字、深度分析，生成结构化知识并存储到私有知识库。

### ✨ 核心特性

- 🎬 **多平台支持** — 抖音、B站、YouTube、快手、TikTok、小红书、视频号
- 🧠 **AI 驱动** — Whisper 语音转文字 + GPT-4 内容理解
- 🔍 **语义搜索** — 基于向量数据库的智能搜索
- 📚 **知识管理** — 结构化存储、分类、标签
- 💻 **桌面应用** — Electron 桌面版，本地运行
- 🆓 **免费方案** — 支持本地 Whisper 模型，无需付费

### 🏗️ 系统架构

```
用户粘贴视频链接 (前端 Next.js)
         ↓
    解析链接 → 识别平台
         ↓
    下载视频 (yt-dlp)
         ↓
    语音转文字 (Whisper)
         ↓
    AI 深度分析 (GPT-4)
         ↓
    知识入库 (ChromaDB)
         ↓
    展示结果 (前端)
```

### 🚀 快速开始

#### 方式一：在线访问

直接访问 **https://video-brain.vercel.app**

#### 方式二：下载桌面应用

1. 前往 [Releases](https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0) 下载 `VideoBrain-v2.6.0-Windows-x64.zip`
2. 解压到任意目录
3. 运行 `electron/electron.exe`

#### 方式三：本地开发

```bash
# 克隆项目
git clone https://github.com/hwl1117/VideoBrain.git
cd VideoBrain

# 一键启动（Windows）
双击 start-local.bat

# 或手动启动
# 终端1：后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# 终端2：前端
cd frontend
npm install
npm run dev
```

### 📁 项目结构

```
VideoBrain/
├── backend/              # Python 后端
│   ├── api/              # FastAPI 接口
│   ├── services/         # 核心服务
│   │   ├── video_downloader.py   # 视频下载
│   │   ├── audio_extractor.py    # 音频提取
│   │   ├── speech_to_text.py     # 语音转文字
│   │   ├── visual_analyzer.py    # 视觉分析
│   │   ├── ai_summarizer.py      # AI 概括
│   │   └── knowledge_base.py     # 知识库管理
│   └── requirements.txt
├── frontend/             # Next.js 前端
│   ├── src/app/          # 页面组件
│   └── package.json
├── electron/             # Electron 桌面应用
│   ├── main.js           # 主进程
│   └── bin/              # Electron 运行时
├── vercel.json           # Vercel 部署配置
└── start-local.bat       # 本地启动脚本
```

### 🔧 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14 + TypeScript + Tailwind CSS |
| 后端 | Python + FastAPI + SQLAlchemy |
| AI | Whisper (语音) + GPT-4 (分析) |
| 数据库 | SQLite + ChromaDB (向量) |
| 桌面 | Electron |
| 部署 | Vercel (前端) + GitHub Releases (App) |

---

## 🇬🇧 English Introduction

### 📖 About

**VideoBrain** is an intelligent knowledge base system for short videos. Paste any short video URL, and the AI automatically extracts content, transcribes speech, performs deep analysis, and generates structured knowledge stored in a private knowledge base.

### ✨ Key Features

- 🎬 **Multi-Platform** — Douyin, Bilibili, YouTube, Kuaishou, TikTok, Xiaohongshu
- 🧠 **AI-Powered** — Whisper speech-to-text + GPT-4 content understanding
- 🔍 **Semantic Search** — Vector database powered intelligent search
- 📚 **Knowledge Management** — Structured storage with categories and tags
- 💻 **Desktop App** — Electron desktop version, runs locally
- 🆓 **Free Option** — Local Whisper model support, no payment required

### 🏗️ Architecture

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

### 🚀 Quick Start

#### Option 1: Online

Visit **https://video-brain.vercel.app**

#### Option 2: Download Desktop App

1. Go to [Releases](https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0)
2. Download `VideoBrain-v2.6.0-Windows-x64.zip`
3. Extract and run `electron/electron.exe`

#### Option 3: Local Development

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

### 📁 Project Structure

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

### 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI + SQLAlchemy |
| AI | Whisper (Speech) + GPT-4 (Analysis) |
| Database | SQLite + ChromaDB (Vector) |
| Desktop | Electron |
| Deploy | Vercel (Web) + GitHub Releases (App) |

### 🔌 API Endpoints

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

---

## 📦 Deployment

### Web (Vercel)

Frontend is deployed to Vercel: **https://video-brain.vercel.app**

Auto-deploys on push to `master` branch.

### Desktop App (GitHub Releases)

Download: [v2.6.0 Release](https://github.com/hwl1117/VideoBrain/releases/tag/v2.6.0)

| File | Size | Description |
|------|------|-------------|
| VideoBrain-v2.6.0-Windows-x64.zip | ~134MB | Windows portable app |

---

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
