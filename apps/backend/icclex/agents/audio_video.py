"""Speech to text. Audio is extracted with ffmpeg first, which keeps the upload under the
transcription size limit and handles containers the API does not accept."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .. import config
from .base import AgentContext, AgentResult, AgentUnavailable, ArtefactDraft, FindingDraft, require_consent
from .llm import transcribe


def _has_audio(path: Path) -> bool:
    proc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                           "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=60)
    return proc.returncode == 0 and proc.stdout.strip() != ""


def _logprob(result: dict) -> float | None:
    segs = [g for g in result["segments"] if g.get("avg_logprob") is not None]
    total = sum(max(g["end"] - g["start"], 0.01) for g in segs)
    return sum(g["avg_logprob"] * max(g["end"] - g["start"], 0.01) for g in segs) / total if segs else None


def _words_per_second(result: dict) -> float:
    return len((result["text"] or "").split()) / max(result["duration"] or 0, 1.0)


def _passes(result: dict, floor: float) -> bool:
    lp = _logprob(result)
    return lp is not None and lp >= floor and _words_per_second(result) >= config.TRANSCRIBE_MIN_WORDS_PER_SECOND


def _expected(language: str | None) -> bool:
    return bool(language) and any(language.lower().startswith(n) for n in config.SPEECH_LANGUAGES.values())


def _trusted_transcript(wav: Path) -> tuple[dict | None, str, list[str]]:
    """Whisper invents fluent text from noise. Accept a transcript only in an expected language and above a
    confidence floor; otherwise retry with each expected language forced, at a stricter floor."""
    tried = []
    result, model = transcribe(wav, "audio.mp3")
    lp = _logprob(result)
    tried.append(f"auto-detected {result['language']}, score {lp if lp is None else round(lp, 2)}, "
                 f"{_words_per_second(result):.2f} words/s")
    if _expected(result["language"]) and _passes(result, config.TRANSCRIBE_MIN_LOGPROB):
        return result, model, tried
    for code, name in config.SPEECH_LANGUAGES.items():
        if result["language"] and result["language"].lower().startswith(name):
            continue  # the auto pass already ran in this language
        forced, model = transcribe(wav, "audio.mp3", language=code)
        lp = _logprob(forced)
        tried.append(f"forced {name}, score {lp if lp is None else round(lp, 2)}, {_words_per_second(forced):.2f} words/s")
        if _passes(forced, config.TRANSCRIBE_FORCED_MIN_LOGPROB):
            return forced, model, tried
    return None, model, tried


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
        result, model, tried = _trusted_transcript(wav)
    if result is None:
        return AgentResult(model=model, notes=[
            "no clear speech in an expected language; listen to the file yourself (" + "; ".join(tried) + ")"])
    text = (result["text"] or "").strip()
    if not any(ch.isalpha() for ch in text):
        return AgentResult(model=model, notes=["no speech was detected"])
    finding = FindingDraft("transcript", {"text": text, "language": result["language"],
                                          "duration_s": result["duration"], "segments": result["segments"],
                                          "confidence_checks": tried}, "inferred")
    return AgentResult(findings=[finding], model=model,
                       artefacts=[ArtefactDraft("transcript_file", "transcript.txt", text.encode())])
