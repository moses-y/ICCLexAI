"""Entities, dates, places and a summary from a document's text. The text is cut at a fixed length
and the finding says so, so a long document is never presented as fully read."""

from .. import config
from .base import AgentContext, AgentResult, AgentUnavailable, FindingDraft, require_consent
from .llm import complete_json

SYSTEM = (
    "You read a document for a person documenting events. Extract only what the text states. Do not "
    "judge guilt, legality or credibility. Reply with JSON: "
    '{"summary": str, "dates": [str], "places": [str], "people_and_organisations": [str], '
    '"events": [str]}. Copy names and dates as written.'
)


def extract_text(ctx: AgentContext) -> str:
    if ctx.mime == "application/pdf":
        import pymupdf

        with pymupdf.open(ctx.path) as doc:
            return "\n".join(page.get_text() for page in doc)
    if ctx.mime.endswith("wordprocessingml.document"):
        from docx import Document

        return "\n".join(p.text for p in Document(str(ctx.path)).paragraphs)
    return ctx.path.read_text(encoding="utf-8", errors="replace")


def run(ctx: AgentContext) -> AgentResult:
    require_consent(ctx)
    text = extract_text(ctx).strip()
    if not text:
        raise AgentUnavailable("the document has no extractable text (it may be a scan)")
    truncated = len(text) > config.MAX_DOCUMENT_CHARS
    data, model = complete_json(SYSTEM, text[:config.MAX_DOCUMENT_CHARS])
    return AgentResult(model=model, findings=[FindingDraft("document_summary", {
        "summary": str(data.get("summary", "")), "dates": data.get("dates", []), "places": data.get("places", []),
        "people_and_organisations": data.get("people_and_organisations", []), "events": data.get("events", []),
        "characters_read": min(len(text), config.MAX_DOCUMENT_CHARS), "characters_total": len(text),
        "truncated": truncated}, "inferred")])
