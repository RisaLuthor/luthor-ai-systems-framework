from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["meta"])
def home():
    return {
        "name": "Luthor AI Systems Framework",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "evaluate": "/evaluate",
        "project": "/project",
    }
