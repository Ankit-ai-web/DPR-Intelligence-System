from fastapi import FastAPI

from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router


app = FastAPI(
    title="DPR Intelligence System",
    description="AI-powered DPR analysis and clearance platform",
    version="1.0.0",
)


app.include_router(users_router)
app.include_router(projects_router)


@app.get("/")
def root():
    return {
        "message": "DPR Intelligence System API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }