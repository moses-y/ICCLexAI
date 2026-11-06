"""Thin Groq wrapper. Every failure becomes AgentUnavailable so a model outage shows up as "not
analysed" rather than as a made-up result."""

import base64
import json

from .. import config
from .base import AgentTransient, AgentUnavailable


def _fail(what: str, exc: Exception) -> AgentUnavailable:
    import groq

    transient = (groq.APIConnectionError, groq.RateLimitError, groq.InternalServerError)
    cls = AgentTransient if isinstance(exc, transient) else AgentUnavailable
    return cls(f"{what} failed: {exc}")


def _client():
    if not config.GROQ_API_KEY:
        raise AgentUnavailable("GROQ_API_KEY is not set")
    from groq import Groq

    return Groq(api_key=config.GROQ_API_KEY, max_retries=config.GROQ_MAX_RETRIES)


def _json_from(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        out = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AgentUnavailable(f"the model did not return valid JSON: {exc}") from exc
    if not isinstance(out, dict):
        raise AgentUnavailable("the model returned JSON that is not an object")
    return out


def _text_model(model: str | None) -> str:
    model = model or config.TEXT_MODEL
    if not model:
        raise AgentUnavailable("ICCLEX_TEXT_MODEL is not set, so no text model is configured")
    return model


def complete_json(system: str, user: str, model: str | None = None) -> tuple[dict, str]:
    model = _text_model(model)
    try:
        resp = _client().chat.completions.create(
            model=model, temperature=0.0, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
    except AgentUnavailable:
        raise
    except Exception as exc:
        raise _fail("text model call", exc) from exc
    return _json_from(resp.choices[0].message.content or ""), model


def complete_text(system: str, messages: list[dict], model: str | None = None) -> tuple[str, str]:
    model = _text_model(model)
    try:
        resp = _client().chat.completions.create(
            model=model, temperature=0.2, messages=[{"role": "system", "content": system}, *messages],
        )
    except AgentUnavailable:
        raise
    except Exception as exc:
        raise _fail("text model call", exc) from exc
    return resp.choices[0].message.content or "", model


def vision_json(system: str, prompt: str, images: list[tuple[bytes, str]]) -> tuple[dict, str]:
    """`images` is a list of (bytes, mime). The images are actually sent, unlike the old agent."""
    if not config.VISION_MODEL:
        raise AgentUnavailable("ICCLEX_VISION_MODEL is not set, so no vision model is configured")
    if len(images) > config.VISION_MAX_IMAGES:
        raise ValueError(f"{len(images)} images in one call; the vision model takes {config.VISION_MAX_IMAGES}")
    content: list[dict] = [{"type": "text", "text": prompt}]
    for data, mime in images:
        b64 = base64.b64encode(data).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
    try:
        resp = _client().chat.completions.create(
            model=config.VISION_MODEL, temperature=0.0, response_format={"type": "json_object"},
            max_completion_tokens=config.VISION_MAX_TOKENS,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": content}],
        )
    except AgentUnavailable:
        raise
    except Exception as exc:
        raise _fail("vision model call", exc) from exc
    return _json_from(resp.choices[0].message.content or ""), config.VISION_MODEL


def transcribe(path, filename: str, language: str | None = None) -> tuple[dict, str]:
    if path.stat().st_size > config.TRANSCRIBE_MAX_BYTES:
        raise AgentUnavailable(
            f"file is {path.stat().st_size // (1024 * 1024)} MB, above the {config.TRANSCRIBE_MAX_BYTES // (1024 * 1024)} MB "
            "transcription limit")
    try:
        with open(path, "rb") as fh:
            out = _client().audio.transcriptions.create(
                file=(filename, fh.read()), model=config.TRANSCRIBE_MODEL,
                response_format="verbose_json", temperature=0.0, **({"language": language} if language else {}),
            )
    except AgentUnavailable:
        raise
    except Exception as exc:
        raise _fail("transcription", exc) from exc
    return {
        "text": out.text, "language": getattr(out, "language", None),
        "duration": getattr(out, "duration", None),
        "segments": [{k: (s[k] if isinstance(s, dict) else getattr(s, k)) for k in ("start", "end", "text", "avg_logprob")}
                     for s in (getattr(out, "segments", None) or [])],
    }, config.TRANSCRIBE_MODEL
