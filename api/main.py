from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.core import settings
from api.routers import fleet, maintenance, model, twin

app = FastAPI(
    title="Maintenance Digital Twin API",
    version="0.1.0",
    description="Research-backed RUL monitoring, what-if simulation and maintenance scheduling.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(fleet.router)
app.include_router(twin.router)
app.include_router(model.router)
app.include_router(maintenance.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


assets_dir = settings.frontend_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str) -> FileResponse:
    requested = settings.frontend_dir / full_path
    if full_path and requested.exists() and requested.is_file():
        return FileResponse(requested)
    return FileResponse(settings.frontend_dir / "index.html")
