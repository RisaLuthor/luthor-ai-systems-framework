from contextlib import asynccontextmanager

from fastapi import FastAPI

from laf.storage.db import init_db

from laf.api.routes.health import router as health_router
from laf.api.routes.evaluate import router as evaluate_router
from laf.api.routes.history import router as history_router
from laf.api.routes.project import router as project_router

PROJECT_URL = "https://github.com/users/RisaLuthor/projects/3"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (nothing yet)

app = FastAPI(
    title="Luthor AI Systems Framework",
    version="0.1.0",
    description=f"**Project Board:** {PROJECT_URL}",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(evaluate_router)
app.include_router(history_router)
app.include_router(project_router)
