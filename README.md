# ICCLexAI

Helps a person turn their own evidence and account into a **package they file themselves** on the ICC
Prosecutor's OTPLink portal. Agents read each file (when and where it was captured, what it shows,
what was said, whether the metadata is consistent) and say how they know. The person confirms, edits
or rejects every finding; only confirmed findings go into the package.

It does **not** submit anything: OTPLink has no public API. It gives no legal advice and never states
that a crime occurred or that the ICC has jurisdiction.

Design, schema and diagrams: [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).
What is still unverified about OTPLink: [docs/otplink-field-map.md](docs/otplink-field-map.md).

## Run it

```bash
docker compose up -d db                       # PostgreSQL 16 + PostGIS on 127.0.0.1:5433
cd apps/backend
pip install -r requirements.txt               # ffmpeg and ffprobe must be on PATH
alembic upgrade head
uvicorn icclex.main:app --port 8002           # API
python -m icclex.worker                       # analysis worker (second terminal)
cd ../frontend && npm install && npm run dev  # http://localhost:5173
```

Or `python launch_icc_system_clean.py` for the API, worker and frontend together, or
`docker compose up --build` for the database, migrations, API and worker.

## Settings

Environment variables, read from `.env` if present (`apps/backend/icclex/config.py`).

| Variable | Purpose |
|---|---|
| `ICCLEX_DATABASE_URL` | default `postgresql+psycopg://icclex:icclex@localhost:5433/icclex` |
| `ICCLEX_STORAGE_ROOT` | where originals and derived files live (default `var/cases`, git-ignored) |
| `GROQ_API_KEY` | needed by every step that calls a model |
| `ICCLEX_TEXT_MODEL` | text model for the interviewer, narrative and documents. **No default.** |
| `ICCLEX_VISION_MODEL` | vision model for descriptions and place clues. **No default.** |
| `ICCLEX_TRANSCRIBE_MODEL` | speech-to-text (default `whisper-large-v3-turbo`, carried over, not re-checked) |
| `ICCLEX_CORS_ORIGINS` | allowed browser origins (default `http://localhost:5173`) |
| `ICCLEX_NOMINATIM_USER_AGENT` | identifies you to OpenStreetMap's geocoder, per its usage policy |
| `VITE_API_URL` | frontend's API address (default `http://localhost:8002`) |

A model that is not set means the step says "not analysed". The text model has no default because the
one the old code used (`llama-3.3-70b-versatile`) returned 404 "does not exist or you do not have access"
on 2026-11-06: name a model your account can use.

## Privacy

- A case needs no account. You get a case key; the server keeps only its hash, so a lost key cannot be recovered.
- Content leaves the server only if the submitter ticks the consent box for that case: images, audio, document text and chat go to the model provider, and GPS points go to OpenStreetMap to name the place. Without consent only the local steps run (file details, consistency checks, distance to the stated place).
- No IP addresses or user agents are stored.
- The map shows points on a blank background; street tiles (which tell openstreetmap.org what area you are viewing) load only if you tick the box.
- The "remove metadata" export option is lossless and covers JPEG and PNG only. Stored originals are never changed.

## Tests

```bash
docker compose up -d db
python -m pytest tests          # needs PostgreSQL; it FAILS rather than skips if it is not reachable
```

They run against a real PostgreSQL + PostGIS database created from the migrations, because the
triggers, constraints and `SKIP LOCKED` queue the design depends on exist nowhere else. The tests
blank the model settings so they cannot reach an outside service.

## Layout

| Path | What lives there |
|---|---|
| `apps/backend/icclex/` | API (`routes.py`), models, worker, agents, narrative, package builder |
| `apps/backend/migrations/` | Alembic: `0001` schema, `0002` integrity triggers |
| `apps/frontend/src/components/case/` | the React UI: files, review, map, account, package |
| `tests/` | API, agent, database-integrity, narrative, package tests |
| `libs/icc_automation/` | older agents, no longer used by the backend; kept until the new agents are accepted |
| `ARCHIVED_REDUNDANT/` | the previous backends, launchers, chat UI and status reports, kept for reference |
