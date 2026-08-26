@echo off
echo Starting E-commerce Chatbot Backend and Frontend...

start "Backend Server (FastAPI)" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
start "Frontend Server (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Done! Server windows launched.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
