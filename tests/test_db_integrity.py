"""The guarantees the design promises, checked against the real schema."""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from icclex import custody, jobs
from icclex.db import engine, session_scope
from icclex.models import AnalysisJob, Case, Evidence, Finding, Narrative, NarrativeClaim, Submitter

from .fixtures import findings, jpeg, upload


def make_case(session) -> Case:
    s = Submitter(token_hash=uuid.uuid4().hex)
    session.add(s)
    session.flush()
    c = Case(submitter_id=s.id)
    session.add(c)
    session.flush()
    return c


def make_evidence(session, case) -> Evidence:
    e = Evidence(case_id=case.id, original_name="a.jpg", mime_sniffed="image/jpeg", size_bytes=3, sha256=uuid.uuid4().hex,
                 storage_uri="x/a.jpg")
    session.add(e)
    session.flush()
    return e


def make_finding(session, case, ev=None, **kw) -> Finding:
    f = Finding(case_id=case.id, evidence_id=ev.id if ev else None, kind=kw.pop("kind", "description"),
                value=kw.pop("value", {"text": "t"}), source=kw.pop("source", "inferred"), **kw)
    session.add(f)
    session.flush()
    return f


def test_evidence_hash_size_and_path_are_write_once():
    with session_scope() as s:
        c = make_case(s)
        ev = make_evidence(s, c)
        eid = ev.id
    for column, value in (("sha256", "'deadbeef'"), ("storage_uri", "'other'"), ("size_bytes", "999")):
        with pytest.raises(DBAPIError, match="write-once"), engine.begin() as conn:
            conn.execute(text(f"UPDATE evidence SET {column} = {value} WHERE id = :i"), {"i": eid})
    with engine.begin() as conn:  # status is allowed to move
        conn.execute(text("UPDATE evidence SET status = 'analysed' WHERE id = :i"), {"i": eid})


def test_custody_log_cannot_be_updated_deleted_or_truncated():
    with session_scope() as s:
        c = make_case(s)
        custody.record(s, c.id, "case_created", actor_type="user", actor_ref="t")
        cid = c.id
    for sql in ("UPDATE custody_event SET actor_ref = 'x'", "DELETE FROM custody_event", "TRUNCATE custody_event"):
        with pytest.raises(DBAPIError, match="append-only"), engine.begin() as conn:
            conn.execute(text(sql))
    with session_scope() as s:
        assert custody.verify_chain(s, cid)[0]


def test_a_findings_content_cannot_be_rewritten_only_its_status():
    with session_scope() as s:
        c = make_case(s)
        f = make_finding(s, c)
        fid = f.id
    for sql in ("UPDATE finding SET value = '{\"text\": \"changed\"}'", "UPDATE finding SET source = 'extracted'",
                "UPDATE finding SET kind = 'gps'"):
        with pytest.raises(DBAPIError, match="cannot be rewritten"), engine.begin() as conn:
            conn.execute(text(f"{sql} WHERE id = :i"), {"i": fid})
    with engine.begin() as conn:
        conn.execute(text("UPDATE finding SET status = 'confirmed' WHERE id = :i"), {"i": fid})


def test_confidence_only_belongs_to_inferred_findings():
    with pytest.raises(IntegrityError, match="ck_finding_confidence_inferred_only"), session_scope() as s:
        c = make_case(s)
        make_finding(s, c, source="extracted", confidence=0.9)


def test_a_narrative_claim_must_cite_a_confirmed_or_edited_finding():
    with session_scope() as s:
        c = make_case(s)
        n = Narrative(case_id=c.id, version=1, body="b")
        s.add(n)
        proposed = make_finding(s, c)
        confirmed = make_finding(s, c, status="confirmed")
        ids = (n.id, proposed.id, confirmed.id)
    with pytest.raises(DBAPIError, match="must cite a confirmed or edited finding"), session_scope() as s:
        s.add(NarrativeClaim(narrative_id=ids[0], sentence_index=0, text="x", finding_id=ids[1]))
    with session_scope() as s:
        s.add(NarrativeClaim(narrative_id=ids[0], sentence_index=0, text="x", finding_id=ids[2]))


def test_the_same_file_cannot_be_in_a_case_twice():
    with pytest.raises(IntegrityError, match="uq_evidence_case_sha256"), session_scope() as s:
        c = make_case(s)
        for _ in range(2):
            s.add(Evidence(case_id=c.id, original_name="a", mime_sniffed="image/jpeg", size_bytes=1, sha256="same", storage_uri="x"))
            s.flush()


def test_two_workers_never_claim_the_same_job(client, case):
    for color in ((1, 1, 1), (2, 2, 2)):
        upload(client, case, f"{color[0]}.jpg", jpeg(color=color), "image/jpeg")
    # Worker A claims and keeps its transaction open; worker B must be handed a different job.
    from icclex.db import SessionLocal

    a, b = SessionLocal(), SessionLocal()
    try:
        first = jobs.claim_next(a)
        second = jobs.claim_next(b)
        assert first is not None and second is not None and first.id != second.id
        claimed = {first.id, second.id}
        for _ in range(10):
            extra = jobs.claim_next(b)
            if extra is None:
                break
            assert extra.id not in claimed
            claimed.add(extra.id)
    finally:
        a.rollback(), b.rollback(), a.close(), b.close()


def test_a_dependent_job_waits_for_the_job_it_depends_on(client, case):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    from icclex.db import SessionLocal

    s = SessionLocal()
    try:
        order = []
        while (job := jobs.claim_next(s)) is not None:
            order.append(job.agent)
            if job.agent == "metadata":  # still 'running': dependents must stay unclaimable
                assert "geolocation" not in order and "integrity" not in order
            job.status = "running"
        # metadata and visual were claimable; geolocation and integrity were not, because metadata never finished
        assert sorted(order) == ["metadata", "visual"]
        s.query(AnalysisJob).filter_by(agent="metadata").update({"status": "done"})
        s.flush()
        rest = []
        while (job := jobs.claim_next(s)) is not None:
            rest.append(job.agent)
        assert sorted(rest) == ["geolocation", "integrity"]
    finally:
        s.rollback()
        s.close()
    assert res


def test_a_job_left_running_by_a_dead_worker_is_requeued(client, case):
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    with session_scope() as s:
        job = jobs.claim_next(s)
        job.started_at = job.started_at.replace(year=2020)
        jid = job.id
    with session_scope() as s:
        assert jobs.requeue_stale(s) == 1
        assert s.get(AnalysisJob, jid).status == "queued"


def test_custody_chain_verifies_and_breaks_when_a_row_is_altered():
    with session_scope() as s:
        c = make_case(s)
        for i in range(4):
            custody.record(s, c.id, "case_created" if i == 0 else "package_built", actor_type="system", actor_ref="t",
                           detail={"n": i})
        cid = c.id
    with session_scope() as s:
        assert custody.verify_chain(s, cid) == (True, None)
    with engine.begin() as conn:  # only possible by disabling the trigger as the table owner, i.e. deliberate tampering
        conn.exec_driver_sql("ALTER TABLE custody_event DISABLE TRIGGER USER")
        conn.execute(text("UPDATE custody_event SET detail = '{\"n\": 99}' WHERE case_id = :c AND detail->>'n' = '2'"), {"c": cid})
        conn.exec_driver_sql("ALTER TABLE custody_event ENABLE TRIGGER USER")
    with session_scope() as s:
        ok, problem = custody.verify_chain(s, cid)
        assert not ok and "does not match" in problem


def test_the_custody_chain_cannot_fork():
    with session_scope() as s:
        c = make_case(s)
        first = custody.record(s, c.id, "case_created", actor_type="system", actor_ref="t")
        cid, prev = c.id, first.prev_event_hash  # a fork reuses the link an existing event already took
    from icclex.models import CustodyEvent

    with pytest.raises(IntegrityError, match="uq_custody_chain_no_fork"), session_scope() as s:
        s.add(CustodyEvent(case_id=cid, event_type="package_built", actor_type="system", actor_ref="x", detail={},
                           prev_event_hash=prev, event_hash="f" * 64, at=first.at))


def test_findings_listing_hides_superseded_rows(client, case, run_jobs):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])
    assert fs and all(f["status"] != "superseded" for f in fs)
