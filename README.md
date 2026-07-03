# VideoBrain

AI-powered short video knowledge base.

Paste a short-video URL, then the system downloads the video, extracts audio,
transcribes speech, analyzes content, and stores structured knowledge for search.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI + SQLAlchemy |
| AI | Whisper + OpenAI vision/text models |
| Database | SQLite + ChromaDB |
| Web deploy | Vercel-compatible frontend + FastAPI backend |

## Local Start

On Windows, double-click:

```text
start-videobrain.bat
```

Or run manually:

```powershell
cd C:\Users\24700\Desktop\AgencySuperpowersProduct
.\start-videobrain.bat
```

The app uses:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Manual Development

Backend:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Build And Check

```powershell
npm --prefix frontend run build
npm --prefix frontend run lint
npm --prefix frontend run test

$env:TESTING='true'
$env:DATABASE_URL='sqlite:///./test.db'
backend\venv\Scripts\python.exe -m pytest tests -q
```

## Environment

Create or update `backend\.env`.

Required for real AI processing:

```env
OPENAI_API_KEY=your-api-key-here
```

Common optional values:

```env
DATABASE_URL=sqlite:///./videobrain.db
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```text
backend/       FastAPI backend and processing services
frontend/      Next.js web UI
tests/         Backend tests
docs/          Project documentation
scripts/       Development helpers
docker-compose.yml
start-videobrain.bat
```
