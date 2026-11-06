"""Settings read from the environment. Everything has a default that works for local development
except the model settings, which are left unset on purpose: an unset model means the agent that
needs it reports "not analysed" instead of guessing one."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("ICCLEX_DATABASE_URL", "postgresql+psycopg://icclex:icclex@localhost:5433/icclex")
STORAGE_ROOT = Path(os.getenv("ICCLEX_STORAGE_ROOT", Path(__file__).resolve().parents[3] / "var" / "cases"))

# Upload ceiling, matching OTPLink's per-file limit ("each file size under 2.0 GB", live form 2026-11-06).
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
# qwen/qwen3.8-27b, the only vision model on the account on 2026-11-06, rejected a 6-frame request with
# 400 "This model supports up to 3 images".
VISION_MAX_IMAGES = int(os.getenv("ICCLEX_VISION_MAX_IMAGES", "3"))
# On Groq's free tier that model allows 1000 output tokens per minute; requests left at the default 2048
# max were refused outright with 429 "Request too large" on 2026-11-06, so every vision call failed.
VISION_MAX_TOKENS = int(os.getenv("ICCLEX_VISION_MAX_TOKENS", "1000"))
# A per-minute rate limit is temporary; the Groq client waits out its retry-after header between attempts.
GROQ_MAX_RETRIES = int(os.getenv("ICCLEX_GROQ_MAX_RETRIES", "5"))
# Carried over from the old transcription agent; not re-checked against the live API.
TRANSCRIBE_MODEL = os.getenv("ICCLEX_TRANSCRIBE_MODEL") or "whisper-large-v3-turbo"
# Groq's Whisper endpoint rejects files above this size.
TRANSCRIBE_MAX_BYTES = 25 * 1024 * 1024
# Spoken languages a transcript is accepted in, as code -> the start of the name Groq's Whisper reports.
# On 2026-11-06 Whisper turned two Nairobi clips into Spanish ("¡Adiós!") and Malay ("Terima kasih"), and
# Swahili speech under noise into Greek letters; a transcript in any other language is withheld.
SPEECH_LANGUAGES = dict(pair.split(":") for pair in os.getenv(
    "ICCLEX_SPEECH_LANGUAGES", "en:english,sw:swahili").split(","))
# Floors set by evals/transcription on 2026-11-06 (180 FLEURS clips: Swahili and English, clean, pink noise and
# crowd babble, plus 30 clips with no speech). At the first guesses (-1.0 auto, -0.5 forced) 57% of the no-speech
# clips got a transcript, mostly "so" over several seconds of noise. Raising the auto floor to -0.6 cost no good
# transcript. Invented text also has almost no words for its length: good transcripts had at least 0.82 words per
# second, invented ones a median of 0.12 (the real case's "Muzika" was one word in 10.5 s). Whisper reports
# invented text as covering the whole clip, and no_speech_prob was 0.00 throughout, so neither can be used.
TRANSCRIBE_MIN_LOGPROB = -0.6
TRANSCRIBE_FORCED_MIN_LOGPROB = -0.5
TRANSCRIBE_MIN_WORDS_PER_SECOND = 0.5

# Nominatim's usage policy requires an identifying User-Agent and at most 1 request per second.
NOMINATIM_USER_AGENT = os.getenv("ICCLEX_NOMINATIM_USER_AGENT", "icclexai-evidence-tool")
NOMINATIM_MIN_INTERVAL_S = 1.0

KEYFRAME_COUNT = 6
MAX_DOCUMENT_CHARS = 24_000
JOB_MAX_ATTEMPTS = 3
# Wait before attempt 2 and 3 of a job that hit a network error or rate limit.
JOB_RETRY_DELAYS_S = (60, 300)
WORKER_POLL_SECONDS = 2.0
# A running job older than this is assumed to belong to a dead worker and is re-queued.
JOB_STALE_AFTER_SECONDS = 15 * 60

# How often the worker re-hashes every stored original and logs the result.
VERIFY_INTERVAL_S = 24 * 3600

# Distance between GPS in a file and the place the submitter says it happened, above which we flag it.
GPS_CONFLICT_KM = 100.0
