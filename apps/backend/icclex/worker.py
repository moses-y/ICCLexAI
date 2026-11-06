"""Claims analysis jobs and runs one agent per job. Agents return findings; this is the only place
that writes them, in one transaction with the job's result and a custody event."""

import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import config, custody, jobs
from .agents import REGISTRY
from .agents.base import AgentContext, AgentResult, AgentTransient, AgentUnavailable
from .db import session_scope
from .models import AnalysisJob, Artefact, Case, Evidence, Finding
from .storage import LocalStorage, get_storage

log = logging.getLogger("icclex.worker")
ACTOR = "worker"


def _case_location(session: Session, case: Case) -> tuple[float, float] | None:
    if case.incident_location is None:
        return None
    from geoalchemy2.shape import to_shape

    point = to_shape(case.incident_location)
    return (point.y, point.x)


def build_context(session: Session, job: AnalysisJob, storage: LocalStorage) -> AgentContext:
    ev = session.get(Evidence, job.evidence_id)
    case = session.get(Case, ev.case_id)
    prior = session.execute(select(Finding).where(
        Finding.evidence_id == ev.id, Finding.status != "rejected")).scalars().all()
    return AgentContext(
        evidence_id=str(ev.id), case_id=str(ev.case_id), path=storage.path(ev.storage_uri), mime=ev.mime_sniffed,
        original_name=ev.original_name, external_consent=case.external_processing_consent,
        prior_findings=[{"kind": f.kind, "value": f.value, "source": f.source} for f in prior],
        case_location=_case_location(session, case))


def store_result(session: Session, job: AnalysisJob, result: AgentResult, storage: LocalStorage) -> None:
    ev = session.get(Evidence, job.evidence_id)
    for draft in result.findings:
        geom = f"SRID=4326;POINT({draft.geom[1]} {draft.geom[0]})" if draft.geom else None
        session.add(Finding(case_id=ev.case_id, evidence_id=ev.id, job_id=job.id, kind=draft.kind, value=draft.value,
                            source=draft.source, confidence=draft.confidence, geom=geom, status="proposed"))
    for art in result.artefacts:
        stored = storage.save_bytes(ev.case_id, f"derived/{ev.id}", art.filename, art.data)
        session.add(Artefact(case_id=ev.case_id, evidence_id=ev.id, job_id=job.id, kind=art.kind,
                             storage_uri=stored.storage_uri, sha256=stored.sha256))


def process_one(storage: LocalStorage | None = None) -> bool:
    """Run one job if there is one. Returns whether it did any work."""
    storage = storage or get_storage()
    with session_scope() as session:
        jobs.requeue_stale(session)
        job = jobs.claim_next(session)
        if job is None:
            return False
        job_id, agent = job.id, job.agent
        ctx = build_context(session, job, storage)  # claim and context in one transaction, then released
    return _run(job_id, agent, ctx, storage)


def _run(job_id: uuid.UUID, agent: str, ctx: AgentContext, storage: LocalStorage) -> bool:
    try:
        result = REGISTRY[agent](ctx)
        error, ok, retry, transient = None, True, False, False
    except AgentTransient as exc:
        result, error, ok, retry, transient = None, str(exc), False, True, True  # network or rate limit: later
    except AgentUnavailable as exc:
        result, error, ok, retry, transient = None, str(exc), False, False, False  # won't succeed on retry: no key, no consent
    except Exception as exc:  # a bug or a bad file: retry, then fail loudly
        log.exception("agent %s crashed on %s", agent, ctx.evidence_id)
        result, error, ok, retry, transient = None, f"{type(exc).__name__}: {exc}", False, True, False

    with session_scope() as session:
        job = session.get(AnalysisJob, job_id)
        ev = session.get(Evidence, job.evidence_id)
        if ok:
            store_result(session, job, result, storage)
            note = "; ".join(result.notes) or None
            jobs.finish_job(session, job, ok=True, error=note, model=result.model, model_version=result.model_version)
            custody.record(session, ev.case_id, "analysed", actor_type="agent", actor_ref=agent, evidence_id=ev.id,
                           detail={"job_id": str(job.id), "findings": len(result.findings), "model": result.model,
                                   "notes": result.notes})
        else:
            jobs.finish_job(session, job, ok=False, error=error, retry=retry, transient=transient)
            if job.status == "failed":
                custody.record(session, ev.case_id, "analysis_failed", actor_type="agent", actor_ref=agent,
                               evidence_id=ev.id, detail={"job_id": str(job.id), "error": error})
        ev.status = jobs.evidence_status(session, ev.id)
        _settle_case(session, ev.case_id)
    return True


def _settle_case(session: Session, case_id: uuid.UUID) -> None:
    """analysing -> review once no evidence in the case is still being analysed."""
    case = session.get(Case, case_id)
    if case.status == "analysing":
        pending = session.execute(select(Evidence.id).where(
            Evidence.case_id == case_id, Evidence.status.in_(("received", "analysing"))).limit(1)).first()
        if pending is None:
            case.status = "review"


def run_forever() -> None:
    from .verify import DailyVerifier

    logging.basicConfig(level=logging.INFO)
    log.info("worker started")
    verifier = DailyVerifier()
    while True:
        try:
            verifier.tick()
            if not process_one():
                time.sleep(config.WORKER_POLL_SECONDS)
        except Exception:
            log.exception("worker loop error")
            time.sleep(config.WORKER_POLL_SECONDS)


if __name__ == "__main__":
    run_forever()
