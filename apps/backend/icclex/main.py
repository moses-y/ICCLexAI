"""ICCLexAI API. Run from apps/backend:  uvicorn icclex.main:app --port 8002"""

import os
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .db import engine
from .routes import router

app = FastAPI(title="ICCLexAI", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ICCLEX_CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"], allow_headers=["*"], expose_headers=["X-Package-SHA256"],
)
app.include_router(router)


def _migration_state() -> tuple[str | None, str]:
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    head = ScriptDirectory.from_config(cfg).get_current_head()
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision(), head


@app.get("/api/health")
def health():
    """Fails (503) when the database is unreachable or migrations are behind, so a stale schema is
    found at deploy time and not on the first upload."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        current, head = _migration_state()
    except Exception as exc:
        return JSONResponse({"status": "unhealthy", "error": str(exc)[:200]}, status_code=503)
    if current != head:
        return JSONResponse({"status": "unhealthy", "error": f"migrations behind: database at {current}, code at {head}"},
                            status_code=503)
    return {"status": "healthy", "schema_revision": current}
