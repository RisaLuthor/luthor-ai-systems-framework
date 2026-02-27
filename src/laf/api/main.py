from fastapi import FastAPI
from laf.api.routes.health import router as health_router
from laf.api.routes.evaluate import router as evaluate_router
from laf.api.routes.project import router as project_router

app = FastAPI(title="Luthor AI Systems Framework", version="0.1.0")

app.include_router(health_router)
app.include_router(evaluate_router)
app.include_router(project_router)
