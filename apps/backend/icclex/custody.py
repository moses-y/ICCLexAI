"""Append-only, hash-chained custody log (the Eurojust/ICC-OTP chain-of-custody annex asks who
handled what, when). Each event stores the hash of the one before it, so deleting or editing a row
breaks the chain. The database also refuses UPDATE and DELETE on the table (migration 0002)."""

import hashlib
import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import GENESIS_HASH, Case, CustodyEvent


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(prev_hash: str, case_id, evidence_id, event_type: str, actor_type: str,
                 actor_ref: str, detail: dict, at: datetime) -> str:
    body = _canonical({
        "case_id": str(case_id), "evidence_id": str(evidence_id) if evidence_id else None,
        "event_type": event_type, "actor_type": actor_type, "actor_ref": actor_ref,
        "detail": detail, "at": at.astimezone(UTC).isoformat(),
    })
    return hashlib.sha256((prev_hash + body).encode()).hexdigest()


def record(session: Session, case_id: uuid.UUID, event_type: str, *, actor_type: str, actor_ref: str,
           evidence_id: uuid.UUID | None = None, detail: dict | None = None) -> CustodyEvent:
    """Locks the case row so two writers cannot both extend the same chain tip."""
    session.execute(select(Case.id).where(Case.id == case_id).with_for_update()).one()
    # The tip is the event nobody points at yet; ordering by clock time would tie within a transaction.
    linked = select(CustodyEvent.prev_event_hash).where(CustodyEvent.case_id == case_id)
    prev = session.execute(
        select(CustodyEvent.event_hash).where(CustodyEvent.case_id == case_id,
                                              CustodyEvent.event_hash.not_in(linked))
    ).scalar()
    prev = prev or GENESIS_HASH
    at = datetime.now(UTC)
    detail = json.loads(_canonical(detail or {}))  # round-trip so the hashed form is what is stored
    event = CustodyEvent(
        case_id=case_id, evidence_id=evidence_id, event_type=event_type, actor_type=actor_type,
        actor_ref=actor_ref, detail=detail, prev_event_hash=prev, at=at,
        event_hash=compute_hash(prev, case_id, evidence_id, event_type, actor_type, actor_ref, detail, at),
    )
    session.add(event)
    session.flush()
    return event


def verify_chain(session: Session, case_id: uuid.UUID) -> tuple[bool, str | None]:
    """Recompute every hash from the genesis value. Returns (ok, first problem)."""
    events = session.execute(select(CustodyEvent).where(CustodyEvent.case_id == case_id)).scalars().all()
    by_prev = {}
    for ev in events:
        if ev.prev_event_hash in by_prev:
            return False, f"chain forks at {ev.prev_event_hash[:12]}"
        by_prev[ev.prev_event_hash] = ev
    prev = GENESIS_HASH
    for _ in events:
        ev = by_prev.get(prev)
        if ev is None:
            return False, "chain is broken: an event is missing or was altered"
        expected = compute_hash(prev, ev.case_id, ev.evidence_id, ev.event_type, ev.actor_type,
                                ev.actor_ref, ev.detail, ev.at)
        if ev.event_hash != expected:
            return False, f"event {ev.id} hash does not match its contents"
        prev = ev.event_hash
    return True, None
