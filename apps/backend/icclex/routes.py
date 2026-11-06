"""HTTP API. Every case route needs the bearer token returned once when the case was created; the
database stores only its hash, and there is no account to recover (anonymous by default)."""

import hashlib
import secrets
import uuid
from datetime import UTC, date, datetime, time

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import config, custody, interview, jobs
from .agents.base import AgentUnavailable
from .db import SessionLocal
from .models import (AnalysisJob, Artefact, Case, CustodyEvent, Evidence, Finding, Narrative, Submitter,
                     SubmissionPackage)
from .package import PackageError, build_package
from .schemas import (BulkAction, CaseCreate, CaseUpdate, FiledRequest, FindingAction, InterviewMessage,
                      PackageRequest, StatedFact)
from .sniff import UNKNOWN, sniff_mime
from .storage import LocalStorage, UploadTooLarge, get_storage

router = APIRouter(prefix="/api")
INLINE_MIMES = ("image/", "audio/", "video/", "application/pdf")


def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_case(case_id: uuid.UUID, authorization: str | None = Header(None), session: Session = Depends(get_session)) -> Case:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing case token")
    case = session.get(Case, case_id)
    submitter = session.get(Submitter, case.submitter_id) if case else None
    # Same answer for "no such case" and "not your case": do not confirm that a case exists.
    if not case or not submitter or not secrets.compare_digest(submitter.token_hash, _token_hash(authorization[7:])):
        raise HTTPException(404, "case not found")
    return case


def _point(lat: float, lon: float) -> str:
    return f"SRID=4326;POINT({lon} {lat})"


def _xy(geog):
    if geog is None:
        return None
    from geoalchemy2.shape import to_shape

    p = to_shape(geog)
    return {"lat": p.y, "lon": p.x}


def _invalidate_outputs(session: Session, case: Case) -> None:
    """A finding changed, so the narrative and package built from the old values no longer match."""
    for n in session.execute(select(Narrative).where(Narrative.case_id == case.id, Narrative.status != "stale")).scalars():
        n.status = "stale"
    for p in session.execute(select(SubmissionPackage).where(SubmissionPackage.case_id == case.id,
                                                             SubmissionPackage.status == "current")).scalars():
        p.status = "stale"
    if case.status == "package_ready":
        case.status = "review"


def _finding_json(f: Finding) -> dict:
    return {"id": str(f.id), "evidence_id": str(f.evidence_id) if f.evidence_id else None, "kind": f.kind,
            "value": f.value, "source": f.source, "confidence": f.confidence, "status": f.status,
            "location": _xy(f.geom), "supersedes_id": str(f.supersedes_id) if f.supersedes_id else None,
            "created_at": f.created_at.isoformat()}


# ---- cases ----------------------------------------------------------------------------------------

@router.post("/cases", status_code=201)
def create_case(body: CaseCreate, session: Session = Depends(get_session)):
    token = secrets.token_urlsafe(32)
    submitter = Submitter(token_hash=_token_hash(token))
    session.add(submitter)
    session.flush()
    case = Case(submitter_id=submitter.id, incident_name=body.incident_name,
                external_processing_consent=body.external_processing_consent)
    session.add(case)
    session.flush()
    custody.record(session, case.id, "case_created", actor_type="user", actor_ref="anonymous",
                   detail={"external_processing_consent": body.external_processing_consent})
    # The token is shown once. There is no recovery: the server holds only its hash.
    return {"case_id": str(case.id), "token": token}


def _case_json(session: Session, case: Case) -> dict:
    evidence = session.execute(select(Evidence).where(Evidence.case_id == case.id).order_by(Evidence.received_at)).scalars().all()
    job_rows = session.execute(select(AnalysisJob).where(AnalysisJob.evidence_id.in_([e.id for e in evidence]))).scalars().all() if evidence else []
    pkg = session.execute(select(SubmissionPackage).where(SubmissionPackage.case_id == case.id)
                          .order_by(SubmissionPackage.version.desc()).limit(1)).scalar()
    period = case.incident_period
    return {
        "id": str(case.id), "status": case.status, "incident_name": case.incident_name,
        "incident_location_text": case.incident_location_text, "incident_location": _xy(case.incident_location),
        "incident_from": period.lower.date().isoformat() if period is not None and period.lower else None,
        "incident_to": period.upper.date().isoformat() if period is not None and period.upper else None,
        "narrative_language": case.narrative_language, "external_processing_consent": case.external_processing_consent,
        "otp_reference": case.otp_reference,
        "evidence": [{"id": str(e.id), "original_name": e.original_name, "mime": e.mime_sniffed, "size_bytes": e.size_bytes,
                      "sha256": e.sha256, "status": e.status, "received_at": e.received_at.isoformat(),
                      "jobs": [{"agent": j.agent, "status": j.status, "error": j.error, "model": j.model}
                               for j in job_rows if j.evidence_id == e.id]} for e in evidence],
        "package": {"version": pkg.version, "status": pkg.status} if pkg else None,
    }


@router.get("/cases/{case_id}")
def read_case(case: Case = Depends(get_case), session: Session = Depends(get_session)):
    return _case_json(session, case)


@router.patch("/cases/{case_id}")
def update_case(body: CaseUpdate, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    from psycopg.types.range import Range

    data = body.model_dump(exclude_unset=True)
    if "incident_lat" in data or "incident_lon" in data:
        lat, lon = data.pop("incident_lat", None), data.pop("incident_lon", None)
        if (lat is None) != (lon is None):
            raise HTTPException(422, "give both latitude and longitude")
        case.incident_location = _point(lat, lon) if lat is not None else None
    if "incident_from" in data or "incident_to" in data:
        start, end = data.pop("incident_from", None), data.pop("incident_to", None)
        if start and end and end < start:
            raise HTTPException(422, "incident_to is before incident_from")
        case.incident_period = Range(datetime.combine(start, time.min, UTC), datetime.combine(end, time.max, UTC)) if start else None
    consent_before = case.external_processing_consent
    for key, value in data.items():
        setattr(case, key, value)
    if case.external_processing_consent != consent_before:
        custody.record(session, case.id, "finding_changed", actor_type="user", actor_ref="anonymous",
                       detail={"setting": "external_processing_consent", "value": case.external_processing_consent})
    session.flush()
    session.refresh(case)  # the location we just assigned is a WKT string until it is read back as a geometry
    return _case_json(session, case)


# ---- evidence -------------------------------------------------------------------------------------

@router.post("/cases/{case_id}/evidence", status_code=201)
def upload_evidence(files: list[UploadFile] = File(...), case: Case = Depends(get_case),
                    session: Session = Depends(get_session), storage: LocalStorage = Depends(get_storage)):
    if case.status == "filed_by_user":
        raise HTTPException(409, "this case is marked as filed; start a new case for new material")
    results = []
    for upload in files:
        evidence_id = uuid.uuid4()
        head: list[bytes] = []

        def chunks(fh=upload.file, head=head):
            while block := fh.read(config.UPLOAD_CHUNK_BYTES):
                if not head:
                    head.append(block[:8192])
                yield block

        try:
            stored = storage.save_stream(case.id, evidence_id, upload.filename or "unnamed", chunks())
        except UploadTooLarge:
            results.append({"original_name": upload.filename, "error": "file is too large", "code": 413})
            continue
        if stored.size_bytes == 0:
            storage.path(stored.storage_uri).unlink(missing_ok=True)
            results.append({"original_name": upload.filename, "error": "file is empty", "code": 400})
            continue
        dup = session.execute(select(Evidence.id).where(Evidence.case_id == case.id, Evidence.sha256 == stored.sha256)).scalar()
        if dup:
            path = storage.path(stored.storage_uri)
            path.chmod(0o644)
            path.unlink()
            results.append({"original_name": upload.filename, "error": "this exact file is already in the case",
                            "code": 409, "evidence_id": str(dup)})
            continue
        mime = sniff_mime(head[0] if head else b"")
        ev = Evidence(id=evidence_id, case_id=case.id, original_name=upload.filename or "unnamed", mime_sniffed=mime,
                      size_bytes=stored.size_bytes, sha256=stored.sha256, storage_uri=stored.storage_uri)
        session.add(ev)
        session.flush()
        custody.record(session, case.id, "received", actor_type="user", actor_ref="anonymous", evidence_id=ev.id,
                       detail={"original_name": ev.original_name, "sha256": ev.sha256, "size_bytes": ev.size_bytes,
                               "mime_sniffed": mime, "mime_claimed": upload.content_type})
        jobs.enqueue_for_evidence(session, ev)
        results.append({"evidence_id": str(ev.id), "original_name": ev.original_name, "sha256": ev.sha256,
                        "size_bytes": ev.size_bytes, "mime": mime, "status": "analysing",
                        "unrecognised_type": mime == UNKNOWN})
    if any("evidence_id" in r and "error" not in r for r in results) and case.status in ("draft", "review", "package_ready"):
        case.status = "analysing"
        _invalidate_outputs(session, case)
        case.status = "analysing"
    return {"results": results}


@router.get("/cases/{case_id}/evidence/{evidence_id}/content")
def evidence_content(evidence_id: uuid.UUID, case: Case = Depends(get_case), session: Session = Depends(get_session),
                     storage: LocalStorage = Depends(get_storage)):
    ev = session.get(Evidence, evidence_id)
    if not ev or ev.case_id != case.id:
        raise HTTPException(404, "evidence not found")
    inline = ev.mime_sniffed.startswith(INLINE_MIMES)
    return FileResponse(storage.path(ev.storage_uri), media_type=ev.mime_sniffed if inline else "application/octet-stream",
                        filename=ev.original_name, content_disposition_type="inline" if inline else "attachment",
                        headers={"X-Content-Type-Options": "nosniff"})


@router.post("/cases/{case_id}/evidence/{evidence_id}/rerun")
def rerun_evidence(evidence_id: uuid.UUID, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    """Re-queue the failed analysis steps for one file, for example after a network outage."""
    if case.status == "filed_by_user":
        raise HTTPException(409, "this case is marked as filed; start a new case for new material")
    ev = session.get(Evidence, evidence_id)
    if not ev or ev.case_id != case.id:
        raise HTTPException(404, "evidence not found")
    agents = jobs.rerun_failed(session, ev)
    if not agents:
        raise HTTPException(409, "no failed analysis steps to re-run for this file")
    _invalidate_outputs(session, case)
    case.status = "analysing"
    custody.record(session, case.id, "reanalysis_requested", actor_type="user", actor_ref="anonymous",
                   evidence_id=ev.id, detail={"agents": agents})
    return {"evidence_id": str(ev.id), "requeued": agents}


# ---- findings -------------------------------------------------------------------------------------

@router.get("/cases/{case_id}/findings")
def list_findings(evidence_id: uuid.UUID | None = None, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    q = select(Finding).where(Finding.case_id == case.id, Finding.status != "superseded")
    if evidence_id:
        q = q.where(Finding.evidence_id == evidence_id)
    return {"findings": [_finding_json(f) for f in session.execute(q.order_by(Finding.created_at)).scalars()]}


def _apply(session: Session, case: Case, f: Finding, action: str, value: dict | None) -> Finding:
    now = datetime.now(UTC)
    result = f
    if action == "confirm":
        f.status, f.confirmed_at = "confirmed", now
    elif action == "reject":
        f.status = "rejected"
    elif action == "edit":
        if not value or not set(f.value) <= set(value):
            raise HTTPException(422, f"an edited value must keep every field of the original: {sorted(f.value)}")
        f.status = "superseded"
        result = Finding(case_id=f.case_id, evidence_id=f.evidence_id, job_id=f.job_id, kind=f.kind, value=value, geom=f.geom,
                         source="stated", confidence=None, status="edited", supersedes_id=f.id, confirmed_at=now)
        session.add(result)
    custody.record(session, case.id, "finding_changed", actor_type="user", actor_ref="anonymous", evidence_id=f.evidence_id,
                   detail={"finding_id": str(f.id), "action": action, "kind": f.kind})
    return result


@router.patch("/cases/{case_id}/findings/{finding_id}")
def change_finding(finding_id: uuid.UUID, body: FindingAction, case: Case = Depends(get_case),
                   session: Session = Depends(get_session)):
    f = session.get(Finding, finding_id)
    if not f or f.case_id != case.id:
        raise HTTPException(404, "finding not found")
    if f.status == "superseded":
        raise HTTPException(409, "this finding was already replaced by an edit")
    out = _apply(session, case, f, body.action, body.value)
    _invalidate_outputs(session, case)
    session.flush()
    return _finding_json(out)


@router.post("/cases/{case_id}/findings/bulk")
def bulk_findings(body: BulkAction, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    ids = [uuid.UUID(i) for i in body.ids]
    found = session.execute(select(Finding).where(Finding.case_id == case.id, Finding.id.in_(ids),
                                                  Finding.status != "superseded")).scalars().all()
    for f in found:
        _apply(session, case, f, body.action, None)
    _invalidate_outputs(session, case)
    return {"changed": len(found), "requested": len(ids)}


@router.post("/cases/{case_id}/facts", status_code=201)
def add_fact(body: StatedFact, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    """A fact the submitter typed themselves. It is theirs, so it starts confirmed."""
    f = Finding(case_id=case.id, kind="stated_fact", source="stated", status="confirmed", confirmed_at=datetime.now(UTC),
                value=body.model_dump())
    session.add(f)
    session.flush()
    custody.record(session, case.id, "finding_changed", actor_type="user", actor_ref="anonymous",
                   detail={"finding_id": str(f.id), "action": "add_statement", "kind": "stated_fact"})
    _invalidate_outputs(session, case)
    return _finding_json(f)


@router.post("/cases/{case_id}/interview")
def interview_turn(body: InterviewMessage, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    if not case.external_processing_consent:
        raise HTTPException(409, "the interviewer sends your messages to a third-party language model; agree to external "
                                 "processing for this case first, or type statements directly")
    try:
        reply, new = interview.turn(session, case.id, body.message)
    except AgentUnavailable as exc:
        raise HTTPException(503, f"the interviewer is unavailable: {exc}") from exc
    return {"reply": reply, "proposed_facts": [_finding_json(f) for f in new]}


# ---- custody, package, filing ---------------------------------------------------------------------

@router.get("/cases/{case_id}/custody")
def read_custody(case: Case = Depends(get_case), session: Session = Depends(get_session)):
    ok, problem = custody.verify_chain(session, case.id)
    events = session.execute(select(CustodyEvent).where(CustodyEvent.case_id == case.id)).scalars().all()
    return {"chain_valid": ok, "problem": problem, "events": [
        {"at": e.at.isoformat(), "event_type": e.event_type, "actor_type": e.actor_type, "actor_ref": e.actor_ref,
         "evidence_id": str(e.evidence_id) if e.evidence_id else None, "detail": e.detail, "event_hash": e.event_hash}
        for e in sorted(events, key=lambda e: e.at)]}


@router.post("/cases/{case_id}/package")
def make_package(body: PackageRequest, case: Case = Depends(get_case), session: Session = Depends(get_session),
                 storage: LocalStorage = Depends(get_storage)):
    try:
        pkg, result = build_package(session, case, storage, strip_metadata_on_export=body.strip_metadata,
                                    use_model=bool(case.external_processing_consent and config.GROQ_API_KEY))
    except PackageError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {"version": pkg.version, "manifest_sha256": pkg.manifest_sha256, "narrative_model": result.narrative.model,
            "removed_from_draft": result.dropped, "status": case.status}


@router.get("/cases/{case_id}/package/download")
def download_package(case: Case = Depends(get_case), session: Session = Depends(get_session),
                     storage: LocalStorage = Depends(get_storage)):
    pkg = session.execute(select(SubmissionPackage).where(SubmissionPackage.case_id == case.id,
                                                          SubmissionPackage.status == "current")).scalar()
    if not pkg:
        raise HTTPException(404, "no current package: build one first (editing a finding makes the old one stale)")
    art = session.get(Artefact, pkg.zip_artefact_id)
    return FileResponse(storage.path(art.storage_uri), media_type="application/zip",
                        filename=f"icclex_package_v{pkg.version}.zip", headers={"X-Package-SHA256": art.sha256})


@router.post("/cases/{case_id}/filed")
def mark_filed(body: FiledRequest, case: Case = Depends(get_case), session: Session = Depends(get_session)):
    """Only the submitter can say they filed. We never submit anything, so we never set this ourselves."""
    if case.status != "package_ready":
        raise HTTPException(409, "build a current package first")
    case.status, case.filed_confirmed_at, case.otp_reference = "filed_by_user", datetime.now(UTC), body.otp_reference
    custody.record(session, case.id, "filed", actor_type="user", actor_ref="anonymous",
                   detail={"otp_reference": body.otp_reference, "note": "reported by the submitter; not verified"})
    return _case_json(session, case)
