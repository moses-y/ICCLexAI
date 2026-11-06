import uuid

import pytest

from sqlalchemy import text

from icclex.agents import llm
from icclex.db import engine

from .fixtures import jpeg, upload


def test_every_case_route_needs_the_cases_own_token(client, case):
    case_id, headers = case
    other_id, other_headers = (lambda b: (b["case_id"], {"Authorization": f"Bearer {b['token']}"}))(client.post("/api/cases", json={}).json())
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    ev_id = client.get(f"/api/cases/{case_id}", headers=headers).json()["evidence"][0]["id"]
    routes = [("get", f"/api/cases/{case_id}"), ("patch", f"/api/cases/{case_id}"), ("get", f"/api/cases/{case_id}/findings"),
              ("get", f"/api/cases/{case_id}/custody"), ("get", f"/api/cases/{case_id}/evidence/{ev_id}/content"),
              ("post", f"/api/cases/{case_id}/package"), ("get", f"/api/cases/{case_id}/package/download"),
              ("post", f"/api/cases/{case_id}/filed")]
    for method, url in routes:
        kw = {"json": {}} if method in ("post", "patch") else {}
        assert getattr(client, method)(url, **kw).status_code == 401, f"{method} {url} without a token"
        assert getattr(client, method)(url, headers={"Authorization": "Bearer wrong"}, **kw).status_code == 404
        # another submitter's valid token must not open this case, and must not reveal that it exists
        assert getattr(client, method)(url, headers=other_headers, **kw).status_code == 404, f"{method} {url} with another case's token"
    assert client.get(f"/api/cases/{uuid.uuid4()}", headers=headers).status_code == 404
    assert other_id != case_id


def test_the_server_keeps_only_a_hash_of_the_token(client):
    body = client.post("/api/cases", json={}).json()
    with engine.connect() as conn:
        stored = conn.execute(text("SELECT token_hash FROM submitter")).scalar()
    assert stored != body["token"] and body["token"] not in stored and len(stored) == 64


def test_evidence_content_is_served_with_the_sniffed_type_and_nosniff(client, case):
    case_id, headers = case
    data = jpeg()
    # A page uploaded as "photo.jpg" must come back as a download, never as something a browser would run.
    upload(client, case, "page.jpg", b"<html><script>alert(1)</script></html>", "image/jpeg")
    upload(client, case, "real.jpg", data, "image/jpeg")
    evs = {e["original_name"]: e for e in client.get(f"/api/cases/{case_id}", headers=headers).json()["evidence"]}
    real = client.get(f"/api/cases/{case_id}/evidence/{evs['real.jpg']['id']}/content", headers=headers)
    assert real.content == data and real.headers["content-type"] == "image/jpeg" and real.headers["x-content-type-options"] == "nosniff"
    page = client.get(f"/api/cases/{case_id}/evidence/{evs['page.jpg']['id']}/content", headers=headers)
    assert page.headers["content-type"] == "application/octet-stream" and "attachment" in page.headers["content-disposition"]


def test_interviewer_needs_consent_and_a_model(client, case, monkeypatch):
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/interview", headers=headers, json={"message": "hello"})
    assert r.status_code == 409 and "third-party" in r.json()["detail"]

    client.patch(f"/api/cases/{case_id}", headers=headers, json={"external_processing_consent": True})
    r = client.post(f"/api/cases/{case_id}/interview", headers=headers, json={"message": "hello"})
    assert r.status_code == 503 and "not set" in r.json()["detail"]
    assert client.get(f"/api/cases/{case_id}/findings", headers=headers).json()["findings"] == []  # nothing invented

    calls = []
    monkeypatch.setattr(llm, "complete_text", lambda system, messages, model=None: (calls.append(messages) or "Where did it happen?", "m"))
    monkeypatch.setattr(llm, "complete_json", lambda system, user, model=None: ({"facts": [
        {"text": "Shots were fired at the market", "when": "2025-06-15", "where": "Gikomba", "who": None}]}, "m"))
    r = client.post(f"/api/cases/{case_id}/interview", headers=headers, json={"message": "Shots were fired at the market on 15 June"}).json()
    (fact,) = r["proposed_facts"]
    assert fact["status"] == "proposed" and fact["source"] == "stated" and fact["value"]["where"] == "Gikomba"


@pytest.mark.parametrize("stated, asks", [("2025-03-03", True), ("2025-06-16", False), ("2025-06-15", False)])
def test_a_date_that_disagrees_with_a_file_is_put_to_the_submitter(client, case, run_jobs, monkeypatch, stated, asks):
    case_id, headers = case
    client.patch(f"/api/cases/{case_id}", headers=headers, json={"external_processing_consent": True})
    upload(client, case, "photo.jpg", jpeg(), "image/jpeg")  # captured 2025-06-15
    run_jobs()
    monkeypatch.setattr(llm, "complete_text", lambda system, messages, model=None: ("Thank you. Anything else?", "m"))
    monkeypatch.setattr(llm, "complete_json", lambda system, user, model=None: ({"facts": [
        {"text": "it happened", "when": stated, "where": None, "who": None}]}, "m"))
    reply = client.post(f"/api/cases/{case_id}/interview", headers=headers, json={"message": "it happened"}).json()["reply"]
    assert ("Which date is right?" in reply) is asks  # one day either side is tolerated (camera clocks, time zones)
    if asks:
        assert "photo.jpg" in reply and "2025-06-15" in reply and stated in reply


def test_health_fails_when_migrations_are_behind(client):
    assert client.get("/api/health").json()["status"] == "healthy"
    with engine.begin() as conn:
        conn.execute(text("UPDATE alembic_version SET version_num = '0001'"))
    try:
        r = client.get("/api/health")
        assert r.status_code == 503 and "migrations behind" in r.json()["error"]
    finally:
        with engine.begin() as conn:
            conn.execute(text("UPDATE alembic_version SET version_num = '0002'"))
    assert client.get("/api/health").status_code == 200


def test_bad_location_input_is_rejected(client, case):
    case_id, headers = case
    assert client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_lat": 95, "incident_lon": 0}).status_code == 422
    assert client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_lat": 1.0}).status_code == 422
    assert client.patch(f"/api/cases/{case_id}", headers=headers,
                        json={"incident_from": "2025-06-20", "incident_to": "2025-06-10"}).status_code == 422
    ok = client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_lat": -1.28, "incident_lon": 36.82,
                                                                      "incident_from": "2025-06-10", "incident_to": "2025-06-12"})
    assert ok.status_code == 200 and ok.json()["incident_location"]["lat"] == -1.28 and ok.json()["incident_from"] == "2025-06-10"
