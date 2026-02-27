from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

PROJECT_URL = "https://github.com/users/RisaLuthor/projects/3"

@router.get("/project", include_in_schema=False)
def project():
    return RedirectResponse(PROJECT_URL)
