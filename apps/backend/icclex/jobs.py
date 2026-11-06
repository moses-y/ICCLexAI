"""The job queue is a table. Workers claim rows with FOR UPDATE SKIP LOCKED, so two workers never
take the same job and there is no Redis to run."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from . import config
from .agents import plan_for
from .models import AnalysisJob, Evidence


def enqueue_for_evidence(session: Session, evidence: Evidence) -> list[AnalysisJob]:
    jobs = [AnalysisJob(evidence_id=evidence.id, agent=agent, depends_on_agent=dep)
            for agent, dep in plan_for(evidence.mime_sniffed)]
    session.add_all(jobs)
    evidence.status = "analysing"
    session.flush()
    return jobs


def requeue_stale(session: Session) -> int:
    """A job still 'running' long after it started belongs to a worker that died."""
    cutoff = datetime.now(UTC) - timedelta(seconds=config.JOB_STALE_AFTER_SECONDS)
    res = session.execute(update(AnalysisJob).where(
        AnalysisJob.status == "running", AnalysisJob.started_at < cutoff).values(status="queued"))
    return res.rowcount


CLAIM_SQL = text("""
    SELECT j.id FROM analysis_job j
    WHERE j.status = 'queued'
      AND (j.depends_on_agent IS NULL OR NOT EXISTS (
            SELECT 1 FROM analysis_job d
            WHERE d.evidence_id = j.evidence_id AND d.agent = j.depends_on_agent
              AND d.status IN ('queued', 'running')))
    ORDER BY j.created_at
    LIMIT 1
    FOR UPDATE OF j SKIP LOCKED
""")


def claim_next(session: Session) -> AnalysisJob | None:
    job_id = session.execute(CLAIM_SQL).scalar()
    if job_id is None:
        return None
    job = session.get(AnalysisJob, job_id)
    job.status = "running"
    job.attempts += 1
    job.started_at = datetime.now(UTC)
    job.error = None
    session.flush()
    return job


def finish_job(session: Session, job: AnalysisJob, *, ok: bool, error: str | None = None,
               model: str | None = None, model_version: str | None = None, retry: bool = False) -> None:
    job.model, job.model_version = model, model_version
    job.error = error
    if not ok and retry and job.attempts < config.JOB_MAX_ATTEMPTS:
        job.status = "queued"
        return
    job.status = "done" if ok else "failed"
    job.finished_at = datetime.now(UTC)


def evidence_status(session: Session, evidence_id: uuid.UUID) -> str:
    statuses = set(session.execute(select(AnalysisJob.status).where(AnalysisJob.evidence_id == evidence_id)).scalars())
    if statuses & {"queued", "running"}:
        return "analysing"
    return "failed" if statuses == {"failed"} else "analysed"
