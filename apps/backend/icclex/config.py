"""Settings read from the environment. Everything has a default that works for local development
except the model settings, which are left unset on purpose: an unset model means the agent that
needs it reports "not analysed" instead of guessing one."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("ICCLEX_DATABASE_URL", "postgresql+psycopg://icclex:icclex@localhost:5433/icclex")
STORAGE_ROOT = Path(os.getenv("ICCLEX_STORAGE_ROOT", Path(__file__).resolve().parents[3] / "var" / "cases"))

# Upload ceiling. OTPLink takes about 4 GB per submission (2023 figure, Phase 0 to re-check).
MAX_UPLOAD_BYTES = int(os.getenv("ICCLEX_MAX_UPLOAD_BYTES", str(2 * 1024**3)))
UPLOAD_CHUNK_BYTES = 1024 * 1024

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or None
# Unset by default, and an empty value counts as unset. A default of "llama-3.3-70b-versatile" (used in
# the old agents) returned 404 "model does not exist or you do not have access" on 2026-11-06, so no
# default is shipped: name a model your account can use, or the step reports "not analysed".
TEXT_MODEL = os.getenv("ICCLEX_TEXT_MODEL") or None
# The old "visual analysis" agent sent a text-only model the image size and called the reply a scene
# analysis; an agent that needs vision must be given a real vision model.
VISION_MODEL = os.getenv("ICCLEX_VISION_MODEL") or None
# Carried over from the old transcription agent; not re-checked against the live API.
TRANSCRIBE_MODEL = os.getenv("ICCLEX_TRANSCRIBE_MODEL") or "whisper-large-v3-turbo"
# Groq's Whisper endpoint rejects files above this size.
TRANSCRIBE_MAX_BYTES = 25 * 1024 * 1024

# Nominatim's usage policy requires an identifying User-Agent and at most 1 request per second.
NOMINATIM_USER_AGENT = os.getenv("ICCLEX_NOMINATIM_USER_AGENT", "icclexai-evidence-tool")
NOMINATIM_MIN_INTERVAL_S = 1.0

KEYFRAME_COUNT = 6
MAX_DOCUMENT_CHARS = 24_000
JOB_MAX_ATTEMPTS = 3
WORKER_POLL_SECONDS = 2.0
# A running job older than this is assumed to belong to a dead worker and is re-queued.
JOB_STALE_AFTER_SECONDS = 15 * 60

# How often the worker re-hashes every stored original and logs the result.
VERIFY_INTERVAL_S = 24 * 3600

# Distance between GPS in a file and the place the submitter says it happened, above which we flag it.
GPS_CONFLICT_KM = 100.0
