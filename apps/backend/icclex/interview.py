"""The context interviewer. The model asks one question at a time and extracts what the person said
into proposed stated_fact findings. It does not give legal advice, judge whether a crime occurred, or
press for detail. Conflicts between what the person says and what a file says are found by plain
date arithmetic, not by the model, and are always put to the person as a question."""

import re
import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .agents import llm
from .models import ChatMessage, Evidence, Finding

DATE_TOLERANCE_DAYS = 1

ASK_SYSTEM = (
    "You help a person describe what they saw or recorded, so it can be given to the International Criminal "
    "Court's Office of the Prosecutor. Be calm and brief. Ask ONE question at a time, in this order of "
    "importance: what happened; when; where; who was involved, by role or description (never press for "
    "names); how they know (saw it, recorded it, were told). The person may be frightened or "
    "traumatised: say they can skip any question, and never push for detail. Do not give legal advice, "
    "do not say whether a crime happened or whether the ICC will act, and do not promise outcomes. Do not ask "
    "for the person's own name or contact details. If they have given you everything useful, say so and "
    "suggest they review the findings. Write in the language they write in."
)
EXTRACT_SYSTEM = (
    "From the person's message, list the facts they state, using their own words as far as possible. Add nothing "
    'they did not say. Reply with JSON: {"facts": [{"text": str, "when": str|null, "where": str|null, '
    '"who": str|null}]}. "when" is an ISO date or date-time (YYYY-MM-DD) only if the message gives enough to '
    "state one, otherwise null. Return an empty list if the message states no facts."
)


def _as_date(text: str | None) -> date | None:
    if not text:
        return None
    m = re.match(r"\d{4}-\d{2}-\d{2}", text)
    try:
        return datetime.strptime(m.group(0), "%Y-%m-%d").date() if m else None
    except ValueError:
        return None


def find_conflicts(session: Session, case_id: uuid.UUID) -> list[str]:
    """Stated dates that do not match any file's capture date. Returns questions for the person."""
    facts = session.execute(select(Finding).where(Finding.case_id == case_id, Finding.kind == "stated_fact",
                                                  Finding.status.in_(("proposed", "confirmed", "edited")))).scalars().all()
    captures = session.execute(select(Finding, Evidence.original_name).join(Evidence, Evidence.id == Finding.evidence_id)
                               .where(Finding.case_id == case_id, Finding.kind == "capture_time",
                                      Finding.status != "rejected")).all()
    dated = [(c, name, _as_date(c.value.get("iso"))) for c, name in captures]
    dated = [d for d in dated if d[2]]
    questions = []
    for fact in facts:
        stated = _as_date(fact.value.get("when"))
        if not stated:
            continue
        for _, name, taken in dated:
            if abs((taken - stated).days) > DATE_TOLERANCE_DAYS:
                questions.append(f"You said this happened on {stated.isoformat()}, but {name} says it was captured on "
                                 f"{taken.isoformat()}. Which date is right? Camera clocks are sometimes wrong, "
                                 "and files are sometimes recorded after the event.")
    return questions


def turn(session: Session, case_id: uuid.UUID, user_text: str) -> tuple[str, list[Finding]]:
    """One interview turn. Raises AgentUnavailable if no model can be reached."""
    history = session.execute(select(ChatMessage).where(ChatMessage.case_id == case_id)
                              .order_by(ChatMessage.created_at)).scalars().all()
    messages = [{"role": m.role, "content": m.content} for m in history[-20:]] + [{"role": "user", "content": user_text}]
    reply, _ = llm.complete_text(ASK_SYSTEM, messages)
    extracted, extractor = llm.complete_json(EXTRACT_SYSTEM, user_text)

    session.add(ChatMessage(case_id=case_id, role="user", content=user_text))
    new = []
    for item in extracted.get("facts", []):
        if str(item.get("text", "")).strip():
            f = Finding(case_id=case_id, kind="stated_fact", source="stated", status="proposed", value={
                "text": str(item["text"]).strip(), "when": item.get("when"), "where": item.get("where"),
                "who": item.get("who"),
                # Until 2026-11-06 the model was dropped here, so a fact a model pulled out of the chat looked
                # the same in the package as one the person typed in; ai_provenance.json needs to tell them apart.
                "extracted_by_model": extractor})
            session.add(f)
            new.append(f)
    session.flush()
    conflicts = find_conflicts(session, case_id)
    if conflicts:
        reply = f"{reply}\n\n{conflicts[0]}"
    session.add(ChatMessage(case_id=case_id, role="assistant", content=reply))
    session.flush()
    return reply, new
