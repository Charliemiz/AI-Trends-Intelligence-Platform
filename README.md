# AI-Trends-Intelligence-Platform
Run Frontend:
- cd frontend
- npm install (install all necessary node packages)
- npm run dev

# Run API on Localhost:
- cd .. (be at project root)
- venv\Scripts\activate (or whatever name of virtual environment is)
- pip install -r requirements.txt
- cd api
- fastapi dev main.py

# Hosted API URL:
### https://ai-trends-intelligence-platform-production.up.railway.app


# (later) update stuff below
# refresh
uvicorn app.main:app --reload
# docs in browser
http://127.0.0.1:8000/api/ingest
