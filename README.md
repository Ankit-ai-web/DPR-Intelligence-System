# DPR Intelligence System

AI-assisted analysis of Detailed Project Reports (DPRs). Upload a text-based PDF, extract its text, generate structured findings with Gemini, and save scores and analysis in PostgreSQL.

## Features
- PDF upload and text extraction with PyMuPDF
- AI-generated executive summary, project/financial/timeline details, risks, missing information, recommendations, and scores
- PostgreSQL persistence for documents and analysis
- Browse, reopen, and delete previously uploaded DPRs
- FastAPI interactive API documentation at `/docs`

> AI output is decision support, not a substitute for qualified engineering, financial, legal, or regulatory review. Scanned/image-only PDFs are not OCR-processed by the current implementation.

## Project structure
- `backend/`: FastAPI API, SQLAlchemy models, Alembic migrations, Gemini analysis
- `frontend/`: React + Vite application
- `pyproject.toml`: Vercel FastAPI entrypoint configuration
- Root `requirements.txt`: Python dependencies used by Vercel's root project

## Environment variables

Backend (Vercel project):
- `DATABASE_URL`: PostgreSQL connection string (Neon is supported)
- `GEMINI_API_KEY`: Google Gemini API key
- `FRONTEND_ORIGINS`: deployed frontend origin, e.g. `https://your-frontend.vercel.app`
- `UPLOAD_DIR`: optional writable directory; default is temporary and ephemeral on serverless platforms

Frontend (separate Vercel project):
- `VITE_API_URL`: deployed backend's base URL, e.g. `https://your-backend.vercel.app` (no trailing slash)

Never commit real credentials or `.env` files. The example environment files contain placeholders only.

## Deploy both parts to Vercel

This repository contains a React frontend and a FastAPI backend. Deploy them as **two Vercel projects** from the same GitHub repository.

### 1. Deploy the FastAPI backend
1. In Vercel, create a project and import this repository.
2. Keep the **Root Directory** at the repository root (do not set it to `frontend`).
3. The root `pyproject.toml` points Vercel to `backend.app.main:app`; root `requirements.txt` contains the backend dependencies.
4. Add these Environment Variables in Vercel Project Settings:
   - `DATABASE_URL` = your managed PostgreSQL connection string
   - `GEMINI_API_KEY` = your Gemini API key
   - `FRONTEND_ORIGINS` = the frontend's production URL (add the preview URL too if needed, comma-separated)
5. Deploy. Verify `https://YOUR-BACKEND.vercel.app/health`, then `/docs`.

### 2. Deploy the React frontend
1. Create a second Vercel project and import the same repository again.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite. Build command: `npm run build`; output directory: `dist`.
4. Add Environment Variable `VITE_API_URL` = the deployed backend URL, with no trailing slash.
5. Deploy and open the frontend URL.

### 3. Verify the integration
- Backend `/health` returns a healthy status.
- Backend `/docs` loads the API docs.
- Frontend can list documents, upload a text-based PDF, run Gemini analysis, retrieve saved analysis, and delete a DPR.
- If the browser reports a CORS error, ensure `FRONTEND_ORIGINS` exactly matches the frontend origin, including `https://` and without a trailing slash, then redeploy the backend.
- If the backend returns a 500, inspect the Vercel function logs and verify `DATABASE_URL` and `GEMINI_API_KEY` are configured for the correct environment (Production/Preview).

## Run locally (PowerShell)

### Backend
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
Set `DATABASE_URL` and `GEMINI_API_KEY` in `backend/.env` first. Run database migrations from `backend/` with `alembic upgrade head` after confirming the database URL and migration configuration. API: `http://127.0.0.1:8000`; docs: `http://127.0.0.1:8000/docs`.

### Frontend
In a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env`.

## Production limitations
- Serverless temporary disk is ephemeral. Uploaded PDF files may not persist across invocations; extracted document text and analysis are stored in PostgreSQL. Use object storage if original PDFs must remain downloadable.
- Long-running AI analysis may encounter serverless function execution limits. If analysis requests time out, deploy the backend to a host that supports longer-running ASGI requests or move AI analysis to a background job.
- Text extraction only; scanned PDFs require OCR.
- Authentication and per-user authorization are not implemented for document routes. Do not expose sensitive reports publicly until access controls are added.
- Validate AI-generated scores and recommendations before using them for real project approvals.
