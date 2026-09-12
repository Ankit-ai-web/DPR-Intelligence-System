from fastapi import FastAPI

app = FastAPI(
    title="DPR Intelligence System",
    description="AI-powered DPR analysis and clearance platform",
    version="1.0.0"
)


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