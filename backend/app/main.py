from fastapi import FastAPI

from app.api.routes.ask import router as ask_router
from app.api.routes.documents import router as documents_router
from app.api.routes.organization import router as organizations_router
from app.api.routes.search import router as search_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(organizations_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(ask_router, prefix="/api/v1")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "service": "kip-api"}
