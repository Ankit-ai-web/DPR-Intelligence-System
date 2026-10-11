from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.api.routes.documents import router as documents_router


app = FastAPI(
    title="DPR Intelligence System",
    description="AI-powered DPR analysis and clearance platform",
    version="1.0.0",
)


# =========================
# CORS CONFIGURATION
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================

app.include_router(documents_router)
app.include_router(users_router)
app.include_router(projects_router)


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "DPR Intelligence System API is running"
    }


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }