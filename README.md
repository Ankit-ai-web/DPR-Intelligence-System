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

## Required environment variables
Backend:
- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini API key
- `FRONTEND_ORIGINS`: optional comma-separated deployed frontend origins, e.g. `https://your-app.vercel.app`
- `UPLOAD_DIR`: optional writable upload path; the default uses a temporary directory and is ephemeral on serverless platforms.

Frontend:
- `VITE_API_URL`: deployed backend base URL, without a trailing slash

Never commit real credentials or `.env` files.

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
Set `DATABASE_URL` and `GEMINI_API_KEY` in `backend/.env` first. Apply migrations from the backend directory with `alembic upgrade head` after confirming the database URL and migration configuration.
API: `http://127.0.0.1:8000`; docs: `http://127.0.0.1:8000/docs`.

### Frontend
In a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env`.

## Deployment guidance
Recommended split deployment:
1. Deploy `backend/` to a Python host that supports ASGI apps and long-running API requests. Use working directory `backend` and start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
2. Set backend `DATABASE_URL`, `GEMINI_API_KEY`, and `FRONTEND_ORIGINS`.
3. Deploy `frontend/` as a separate Vercel project with root directory `frontend` and build command `npm run build`. Set `VITE_API_URL` to the deployed backend URL.
4. Use managed PostgreSQL (e.g. Neon) and run database migrations against it.
5. Test `/health`, `/docs`, PDF upload, AI analysis, saved analysis retrieval, and deletion after deployment.

The repository includes a Vercel FastAPI entrypoint hint, but serverless local disk is ephemeral and AI analysis may exceed a serverless request limit. Do not rely on local uploads surviving restarts; use object storage if original PDFs must persist.

## Current limitations
- Text extraction only; scanned PDFs require OCR.
- Authentication and per-user authorization are not implemented for document routes.
- Uploaded file bytes use local runtime storage by default; production should use durable object storage.
- Validate AI-generated scores and recommendations before using them for real project approvals.
