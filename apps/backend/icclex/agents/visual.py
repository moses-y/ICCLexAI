"""Neutral description of what is visible. The model is sent the actual pixels (the previous agent
sent only the image's dimensions to a text model). People are described, never identified."""

from .base import AgentContext, AgentResult, ArtefactDraft, AgentUnavailable, FindingDraft, require_consent
from .. import config
from .frames import downscaled_jpeg, extract_keyframes
from .llm import vision_json

SYSTEM = (
    "You describe photos and video frames for a human who is documenting events. Rules: describe only what "
    "is visible, in neutral words. Count people but never identify anyone, and do not guess ethnicity, "
    "nationality, affiliation or intent. Describe uniforms, insignia, weapons, injuries, vehicles and damage "
    "literally (for example 'a person in a green uniform holding a long object') and say when you cannot "
    "tell. Copy any visible text exactly, with its language if you can tell. Reply with JSON: "
    '{"description": str, "people_count": int|null, "visible_text": [{"text": str, "language": str|null}], '
    '"notable_elements": [str], "uncertainties": [str]}.'
)


def _findings(data: dict, extra: dict) -> list[FindingDraft]:
    out = [FindingDraft("description", {
        "text": str(data.get("description", "")), "people_count": data.get("people_count"),
        "notable_elements": [str(x) for x in data.get("notable_elements", [])],
        "uncertainties": [str(x) for x in data.get("uncertainties", [])], **extra}, "inferred")]
    for item in data.get("visible_text", []):
        if item.get("text"):
            out.append(FindingDraft("visible_text", {"text": str(item["text"]), "language": item.get("language"),
                                                     **extra}, "inferred"))
    return out


def run(ctx: AgentContext) -> AgentResult:
    require_consent(ctx)
    if ctx.mime.startswith("image/"):
        data, model = vision_json(SYSTEM, "Describe this image.", [(downscaled_jpeg(ctx.path), "image/jpeg")])
        return AgentResult(findings=_findings(data, {}), model=model)
    if ctx.mime.startswith("video/"):
        frames = extract_keyframes(ctx.path, config.KEYFRAME_COUNT)
        if not frames:
            raise AgentUnavailable("no frames could be read from the video")
        findings, artefacts, model = [], [], None
        for i in range(0, len(frames), config.VISION_MAX_IMAGES):
            batch = frames[i:i + config.VISION_MAX_IMAGES]
            times = [t for t, _ in batch]
            data, model = vision_json(
                SYSTEM, f"These are frames from one video at {times} seconds. Describe what happens across them.",
                [(jpg, "image/jpeg") for _, jpg in batch])
            findings += _findings(data, {"frame_times_s": times})
        artefacts = [ArtefactDraft("keyframe", f"frame_{t:08.2f}s.jpg", jpg) for t, jpg in frames]
        return AgentResult(findings=findings, artefacts=artefacts, model=model)
    raise AgentUnavailable(f"visual description does not apply to {ctx.mime}")
