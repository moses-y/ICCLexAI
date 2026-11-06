"""Tests run against a real PostgreSQL + PostGIS database, not SQLite: the triggers, constraints and
SKIP LOCKED queue that the design depends on do not exist anywhere else. The database is created
fresh by running the migrations. If it is unreachable the suite FAILS; it never skips, because a
skipped suite looks like a passing one."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import psycopg
import pytest

ADMIN_URL = os.getenv("ICCLEX_TEST_ADMIN_URL", "postgresql://icclex:icclex@localhost:5433/postgres")
TEST_DB = "icclex_test"
STORAGE = Path(tempfile.mkdtemp(prefix="icclex-test-storage-"))

# Must be set before icclex is imported anywhere: its settings are read at import time.
os.environ["ICCLEX_DATABASE_URL"] = f"postgresql+psycopg://icclex:icclex@localhost:5433/{TEST_DB}"
os.environ["ICCLEX_STORAGE_ROOT"] = str(STORAGE)
# Empty, not removed: icclex.config calls load_dotenv(), which would otherwise load the developer's real
# key from .env and let a test reach Groq (one interview test did, on 2026-11-06, before this was set).
for _name in ("GROQ_API_KEY", "ICCLEX_TEXT_MODEL", "ICCLEX_VISION_MODEL", "ICCLEX_TRANSCRIBE_MODEL"):
    os.environ[_name] = ""

BACKEND = Path(__file__).resolve().parents[1] / "apps" / "backend"


@pytest.fixture(scope="session", autouse=True)
def database():
    try:
        with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
            conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
            conn.execute(f"CREATE DATABASE {TEST_DB}")
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is not reachable at {ADMIN_URL}: {exc}\n"
                    "Start it with: docker compose up -d db   (see docker-compose.yml)", pytrace=False)
    proc = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=BACKEND, capture_output=True, text=True,
                          env=os.environ)
    assert proc.returncode == 0, proc.stderr
    yield
    shutil.rmtree(STORAGE, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean(database):
    yield
    from icclex.db import engine

    with engine.begin() as conn:
        conn.exec_driver_sql("ALTER TABLE custody_event DISABLE TRIGGER USER")  # append-only for the app, not for test cleanup
        conn.exec_driver_sql("TRUNCATE submitter, \"case\", evidence, analysis_job, finding, artefact, custody_event, "
                             "timeline_event, timeline_event_finding, narrative, narrative_claim, submission_package, "
                             "chat_message CASCADE")
        conn.exec_driver_sql("ALTER TABLE custody_event ENABLE TRIGGER USER")
    shutil.rmtree(STORAGE, ignore_errors=True)
    STORAGE.mkdir(exist_ok=True)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from icclex.main import app

    return TestClient(app)


@pytest.fixture
def case(client):
    """A new case: (case_id, auth headers)."""
    body = client.post("/api/cases", json={}).json()
    return body["case_id"], {"Authorization": f"Bearer {body['token']}"}


@pytest.fixture
def run_jobs():
    """Run the worker until the queue is empty. Returns how many jobs ran."""
    from icclex import worker

    def _run(limit: int = 100) -> int:
        n = 0
        while n < limit and worker.process_one():
            n += 1
        return n

    return _run
