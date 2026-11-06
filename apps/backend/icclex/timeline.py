"""Timeline from confirmed findings: when the files were captured and what the submitter says happened."""

import re
import uuid
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import Evidence, Finding, TimelineEvent, TimelineEventFinding
from .narrative import citable_findings


def _parse(text: str | None) -> tuple[datetime | None, str]:
    if not text:
        return None, "unknown"
    if re.fullmatch(r"\d{4}-\d{2}", text):
        return datetime.fromisoformat(text + "-01"), "month"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return datetime.fromisoformat(text), "day"
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")), "exact"
    except ValueError:
        return None, "unknown"


def rebuild_timeline(session: Session, case_id: uuid.UUID) -> list[TimelineEvent]:
    old_ids = session.execute(select(TimelineEvent.id).where(TimelineEvent.case_id == case_id)).scalars().all()
    if old_ids:
        session.execute(delete(TimelineEventFinding).where(TimelineEventFinding.timeline_event_id.in_(old_ids)))
        session.execute(delete(TimelineEvent).where(TimelineEvent.id.in_(old_ids)))
    names = {e.id: e.original_name for e in session.execute(select(Evidence).where(Evidence.case_id == case_id)).scalars()}
    events: list[TimelineEvent] = []
    for f in citable_findings(session, case_id):
        if f.kind == "capture_time":
            when, precision = _parse(f.value.get("iso"))
            label = f"{names.get(f.evidence_id, 'A file')} was captured"
        elif f.kind == "stated_fact" and f.value.get("when"):
            when, precision = _parse(f.value["when"])
            label = f.value["text"]
        else:
            continue
        ev = TimelineEvent(case_id=case_id, occurred_at=when, time_precision=precision, label=label)
        ev.findings.append(TimelineEventFinding(finding_id=f.id))
        session.add(ev)
        events.append(ev)
    session.flush()
    return sorted(events, key=lambda e: (e.occurred_at is None, e.occurred_at.replace(tzinfo=None) if e.occurred_at else 0))
