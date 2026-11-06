"""The narrative may only say what a confirmed finding supports, and cites the finding for every
sentence. On 2026-11-05 the case document was a fixed template that stated "Cryptographic hashing
applied", "clear jurisdiction" and "PROCEED TO FORMAL INVESTIGATION" for every case. The tool does not
make legal conclusions: sentences that do are dropped and reported, never silently kept."""

import re
import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from .agents import llm
from .agents.base import AgentUnavailable
from .models import CITABLE_STATUSES, Evidence, Finding, Narrative, NarrativeClaim

LEGAL_CONCLUSION = re.compile(
    r"prima facie|clear(ly)?\s+(has\s+)?jurisdiction|formal investigation|\bguilty\b|\bperpetrators?\s+(are|is|were)\b|"
    r"\b(constitutes?|amounts?\s+to|is|are|were|was)\s+(a\s+|an\s+)?(war crimes?|crimes?\s+against\s+humanity|genocide)\b|"
    r"\bcommitted\s+(a\s+)?(war crimes?|crimes?\s+against\s+humanity|genocide)\b|\bproceed to\b|\bshould be prosecuted\b",
    re.I)

SOURCE_LEAD = {"extracted": "From the file", "inferred": "An AI model suggested, and the submitter confirmed",
               "stated": "The submitter states"}


def render_finding(f: Finding) -> str:
    v = f.value
    k = f.kind
    if k == "capture_time":
        return f"capture time {v['iso']} ({'with' if v.get('tz_known') else 'without'} a time zone), read from {v.get('field')}"
    if k == "gps":
        return f"GPS coordinates {v['lat']:.5f}, {v['lon']:.5f} are recorded in the file ({v.get('field')})"
    if k == "place":
        return f"the GPS point resolves to {v.get('display_name')} (OpenStreetMap lookup)"
    if k == "place_candidate":
        return f"the place may be {v['place']}, because: {'; '.join(v.get('reasons', []))}"
    if k == "description":
        return f"the content shows: {v['text']}"
    if k == "visible_text":
        return f"visible text reads: \"{v['text']}\"" + (f" ({v['language']})" if v.get("language") else "")
    if k == "transcript":
        text = v["text"]
        return f"the audio was transcribed ({v.get('language')}) as: \"{text[:600]}{'…' if len(text) > 600 else ''}\""
    if k == "document_summary":
        return f"the document says: {v['summary']}"
    if k == "device":
        return "recording device details: " + ", ".join(f"{a} {b}" for a, b in v.items())
    if k == "file_properties":
        return "file properties: " + ", ".join(f"{a} {b}" for a, b in v.items() if b is not None and a != "streams")
    if k in ("integrity_flag", "geo_conflict"):
        return v["detail"]
    if k == "stated_fact":
        return v["text"]
    return f"{k}: {v}"


def attribute(f: Finding) -> str:
    text = render_finding(f)
    lead = SOURCE_LEAD[f.source] if f.status != "edited" else "The submitter wrote"
    return f"{lead}: {text}."


@dataclass
class NarrativeResult:
    narrative: Narrative
    dropped: list[dict] = field(default_factory=list)  # sentences removed, with why: shown to the submitter


def citable_findings(session: Session, case_id: uuid.UUID) -> list[Finding]:
    return list(session.execute(select(Finding).where(
        Finding.case_id == case_id, Finding.status.in_(CITABLE_STATUSES)).order_by(Finding.created_at)).scalars())


SYSTEM = (
    "You write the factual account section of a submission to the ICC Office of the Prosecutor, from a numbered "
    "list of confirmed facts. Rules: use only the facts given; cite every sentence with the ids of the facts that "
    "support it; say where a fact came from (the file, an AI suggestion the submitter confirmed, or the submitter's "
    "own statement); never state or imply that a crime was committed, that anyone is guilty, that the ICC has "
    "jurisdiction, or that an investigation should open; you may say what the material shows or what the "
    "submitter reports. Reply with JSON: {\"sentences\": [{\"text\": str, \"cites\": [\"F1\", ...]}]}."
)


def _deterministic(findings: list[Finding]) -> list[tuple[str, list[Finding]]]:
    return [(attribute(f), [f]) for f in findings]


def build_narrative(session: Session, case_id: uuid.UUID, *, use_model: bool) -> NarrativeResult:
    findings = citable_findings(session, case_id)
    if not findings:
        raise ValueError("there are no confirmed findings to write from")
    by_label = {f"F{i}": f for i, f in enumerate(findings, start=1)}
    names = {e.id: e.original_name for e in session.execute(select(Evidence).where(Evidence.case_id == case_id)).scalars()}
    dropped: list[dict] = []
    model = None
    sentences: list[tuple[str, list[Finding]]] = []

    if use_model:
        listing = "\n".join(f"[{label}] ({f.source}; file: {names.get(f.evidence_id, 'submitter statement')}) {render_finding(f)}"
                            for label, f in by_label.items())
        try:
            data, model = llm.complete_json(SYSTEM, listing)
            for item in data.get("sentences", []):
                cited = [by_label[c] for c in item.get("cites", []) if c in by_label]
                text = str(item.get("text", "")).strip()
                if not text:
                    continue
                if not cited:
                    dropped.append({"text": text, "reason": "no citation to a confirmed finding"})
                elif LEGAL_CONCLUSION.search(text):
                    dropped.append({"text": text, "reason": "states a legal conclusion, which this tool does not make"})
                else:
                    sentences.append((text, cited))
        except AgentUnavailable as exc:
            dropped.append({"text": "(whole narrative)", "reason": f"model unavailable ({exc}); factual record used instead"})
            model = None
    if not sentences:
        sentences = _deterministic(findings)

    last = session.execute(select(Narrative.version).where(Narrative.case_id == case_id)
                           .order_by(Narrative.version.desc()).limit(1)).scalar() or 0
    for old in session.execute(select(Narrative).where(Narrative.case_id == case_id, Narrative.status != "stale")).scalars():
        old.status = "stale"
    narrative = Narrative(case_id=case_id, version=last + 1, model=model, status="draft",
                          body=" ".join(t for t, _ in sentences))
    session.add(narrative)
    session.flush()
    for idx, (text, cited) in enumerate(sentences):
        for f in cited:
            session.add(NarrativeClaim(narrative_id=narrative.id, sentence_index=idx, text=text, finding_id=f.id))
    session.flush()
    return NarrativeResult(narrative, dropped)
