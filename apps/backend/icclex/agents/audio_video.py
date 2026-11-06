"""Speech to text. Audio is extracted with ffmpeg first, which keeps the upload under the
transcription size limit and handles containers the API does not accept."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import AgentContext, AgentResult, AgentUnavailable, ArtefactDraft, FindingDraft, require_consent
from .llm import transcribe


def _has_audio(path: Path) -> bool:
    proc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                           "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=60)
    return proc.returncode == 0 and proc.stdout.strip() != ""


def run(ctx: AgentContext) -> AgentResult:
    require_consent(ctx)
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise AgentUnavailable("ffmpeg is not installed")
    if not _has_audio(ctx.path):
        return AgentResult(notes=["the file has no audio track"])
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.mp3"
        proc = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ctx.path), "-vn", "-ac", "1", "-ar", "16000",
                               "-b:a", "48k", str(wav)], capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise AgentUnavailable(f"ffmpeg could not extract audio: {proc.stderr.strip()[:200]}")
        result, model = transcribe(wav, "audio.mp3")
    text = (result["text"] or "").strip()
    if not text:
        return AgentResult(model=model, notes=["no speech was detected"])
    finding = FindingDraft("transcript", {"text": text, "language": result["language"],
                                          "duration_s": result["duration"], "segments": result["segments"]}, "inferred")
    return AgentResult(findings=[finding], model=model,
                       artefacts=[ArtefactDraft("transcript_file", "transcript.txt", text.encode())])
