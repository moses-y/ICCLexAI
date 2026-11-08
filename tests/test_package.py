"""The whole path through the API: upload, analyse, confirm, build the package, check what is in it."""

import csv
import hashlib
import io
import json
import zipfile


from icclex import narrative

from .fixtures import findings, jpeg, upload


def confirm_all(client, case, evidence_id=None):
    case_id, headers = case
    ids = [f["id"] for f in findings(client, case, evidence_id) if f["status"] == "proposed"]
    r = client.post(f"/api/cases/{case_id}/findings/bulk", headers=headers, json={"ids": ids, "action": "confirm"})
    assert r.status_code == 200 and r.json()["changed"] == len(ids)
    return ids


def build(client, case, consent=True):
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/package", headers=headers, json={"consent_files_as_they_are": consent})
    return r


def open_zip(client, case) -> zipfile.ZipFile:
    case_id, headers = case
    r = client.get(f"/api/cases/{case_id}/package/download", headers=headers)
    assert r.status_code == 200
    assert r.headers["X-Package-SHA256"] == hashlib.sha256(r.content).hexdigest()
    return zipfile.ZipFile(io.BytesIO(r.content))


def prepared_case(client, case, run_jobs, data=None):
    data = data or jpeg()
    res = upload(client, case, "photo.jpg", data, "image/jpeg")
    run_jobs()
    confirm_all(client, case)
    case_id, headers = case
    client.post(f"/api/cases/{case_id}/facts", headers=headers, json={"text": "I took this photo at the market.", "when": "2025-06-15"})
    client.patch(f"/api/cases/{case_id}", headers=headers,
                 json={"incident_from": "2025-06-15", "incident_to": "2025-06-15", "incident_location_text": "Nairobi"})
    return res, data


def test_package_holds_a_manifest_that_matches_the_files_but_no_copy_of_them(client, case, run_jobs):
    res, data = prepared_case(client, case, run_jobs)
    r = build(client, case)
    assert r.status_code == 200, r.text

    z = open_zip(client, case)
    names = set(z.namelist())
    assert {"README_FIRST.txt", "manifest.json", "manifest.csv", "summary.pdf", "evidence_map.geojson", "custody_log.csv",
            "otplink_fields.md", "ai_provenance.json"} <= names
    manifest = json.loads(z.read("manifest.json"))
    (row,) = manifest["evidence"]
    assert row["sha256"] == hashlib.sha256(data).hexdigest() == res["sha256"]
    # The package is the person's record; OTPLink gets the stored originals, so no copy goes in the zip.
    assert not [n for n in names if n.startswith("originals/")]
    assert "holds no copy of your files" in z.read("README_FIRST.txt").decode()
    assert hashlib.sha256(z.read("manifest.json")).hexdigest() == r.json()["manifest_sha256"]
    assert manifest["custody_chain_valid"] is True
    assert z.read("summary.pdf")[:5] == b"%PDF-"
    rows = list(csv.DictReader(io.StringIO(z.read("manifest.csv").decode())))
    assert rows[0]["sha256"] == res["sha256"]


def test_geojson_and_fields_use_only_confirmed_data_and_say_it_is_not_filed(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    build(client, case)
    z = open_zip(client, case)
    (feature,) = json.loads(z.read("evidence_map.geojson"))["features"]
    assert feature["geometry"]["coordinates"][0] > 36 and feature["geometry"]["coordinates"][1] < -1
    fields = z.read("otplink_fields.md").decode()
    assert "live OTPLink form" in fields and "## Factual Summary" in fields and "photo.jpg" in z.read("manifest.json").decode()
    assert "has not been submitted to anyone" in z.read("README_FIRST.txt").decode()


def test_every_sentence_is_cited_and_nothing_states_a_legal_conclusion(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    r = build(client, case)
    assert r.json()["narrative_model"] is None  # no consent and no key: the plain attributed record, no model involved
    from icclex.db import session_scope
    from icclex.models import Narrative, NarrativeClaim

    with session_scope() as s:
        n = s.query(Narrative).filter_by(status="approved").one()
        claims = s.query(NarrativeClaim).filter_by(narrative_id=n.id).all()
        from icclex.models import Finding

        citable = s.query(Finding).filter(Finding.status.in_(("confirmed", "edited")),
                                          Finding.kind.notin_(narrative.NARRATIVE_EXCLUDED_KINDS)).count()
        assert claims and all(c.finding_id for c in claims)
        assert len({c.sentence_index for c in claims}) == citable  # plain record: one cited sentence per confirmed finding
        assert all(c.text in n.body for c in claims)
        assert not narrative.LEGAL_CONCLUSION.search(n.body)
        assert "From the file" in n.body and "The submitter states" in n.body


def test_unconfirmed_findings_never_reach_the_package(client, case, run_jobs):
    res = upload(client, case, "photo.jpg", jpeg(), "image/jpeg")
    run_jobs()
    case_id, headers = case
    fs = findings(client, case, res["evidence_id"])
    only = next(f for f in fs if f["kind"] == "capture_time")
    client.patch(f"/api/cases/{case_id}/findings/{only['id']}", headers=headers, json={"action": "confirm"})
    client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_from": "2025-06-15", "incident_location_text": "Nairobi"})
    build(client, case)
    z = open_zip(client, case)
    assert json.loads(z.read("evidence_map.geojson"))["features"] == []  # the GPS finding was never confirmed
    assert json.loads(z.read("manifest.json"))["evidence"][0]["confirmed_findings"] == 1


def test_a_package_needs_at_least_one_confirmed_finding(client, case, run_jobs):
    upload(client, case, "photo.jpg", jpeg(), "image/jpeg")
    run_jobs()
    r = build(client, case)
    assert r.status_code == 409 and "confirm at least one finding" in r.json()["detail"]


def test_a_package_cannot_be_built_while_analysis_is_still_running(client, case):
    upload(client, case, "photo.jpg", jpeg(), "image/jpeg")
    assert "still being analysed" in build(client, case).json()["detail"]


def test_editing_a_finding_after_the_package_makes_it_stale(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    build(client, case)
    case_id, headers = case
    assert client.get(f"/api/cases/{case_id}", headers=headers).json()["status"] == "package_ready"

    dev = next(f for f in findings(client, case) if f["kind"] == "capture_time")
    edited = client.patch(f"/api/cases/{case_id}/findings/{dev['id']}", headers=headers,
                          json={"action": "edit", "value": {**dev["value"], "iso": "2025-06-16T09:00:00+03:00"}})
    assert edited.status_code == 200 and edited.json()["status"] == "edited" and edited.json()["source"] == "stated"
    assert edited.json()["supersedes_id"] == dev["id"]

    case_json = client.get(f"/api/cases/{case_id}", headers=headers).json()
    assert case_json["status"] == "review" and case_json["package"]["status"] == "stale"
    assert client.get(f"/api/cases/{case_id}/package/download", headers=headers).status_code == 404
    assert dev["id"] not in {f["id"] for f in findings(client, case)}  # the replaced row is hidden, not deleted

    assert build(client, case).status_code == 200  # rebuilding works and uses the corrected value
    from icclex.db import session_scope
    from icclex.models import Narrative

    with session_scope() as s:
        current = s.query(Narrative).filter_by(status="approved").one()
        assert current.version == 2 and "The submitter wrote: capture time 2025-06-16T09:00:00+03:00" in current.body
        assert "2025-06-15T10:30" not in current.body


def test_an_edit_must_keep_the_findings_fields(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    case_id, headers = case
    dev = next(f for f in findings(client, case) if f["kind"] == "device")
    r = client.patch(f"/api/cases/{case_id}/findings/{dev['id']}", headers=headers, json={"action": "edit", "value": {"make": "x"}})
    assert r.status_code == 422


def test_marking_a_case_filed_needs_a_current_package_and_is_the_submitters_word(client, case, run_jobs):
    case_id, headers = case
    assert client.post(f"/api/cases/{case_id}/filed", headers=headers, json={}).status_code == 409
    prepared_case(client, case, run_jobs)
    build(client, case)
    r = client.post(f"/api/cases/{case_id}/filed", headers=headers, json={"otp_reference": "OTP-TEST-1"})
    assert r.status_code == 200 and r.json()["status"] == "filed_by_user" and r.json()["otp_reference"] == "OTP-TEST-1"
    custody = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()
    filed = next(e for e in custody["events"] if e["event_type"] == "filed")
    assert filed["actor_type"] == "user" and "not verified" in filed["detail"]["note"] and custody["chain_valid"]
    up = client.post(f"/api/cases/{case_id}/evidence", headers=headers, files={"files": ("x.jpg", jpeg(color=(9, 9, 9)), "image/jpeg")})
    assert up.status_code == 409


def test_the_custody_log_in_the_package_matches_the_database(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    build(client, case)
    case_id, headers = case
    z = open_zip(client, case)
    rows = list(csv.DictReader(io.StringIO(z.read("custody_log.csv").decode())))
    types = [r["event_type"] for r in rows]
    assert types[0] == "case_created" and "received" in types and "analysed" in types and "finding_changed" in types
    assert all(len(r["event_hash"]) == 64 for r in rows)


def test_ai_provenance_names_who_produced_each_included_finding(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    build(client, case)
    z = open_zip(client, case)
    prov = json.loads(z.read("ai_provenance.json"))
    assert "AI use:" in z.read("README_FIRST.txt").decode()
    producers = {r["produced_by"]["type"] for r in prov["findings"]}
    # Tests run without a model: EXIF facts come from a deterministic step, the typed fact from the submitter.
    assert {"deterministic", "submitter"} <= producers and "model" not in producers
    assert all(r["human_review"] and r["evidence"] in (None, "E1") for r in prov["findings"])
    assert prov["models"] == [] and prov["narrative"]["drafted_by_model"] is None
    typed = [r for r in prov["findings"] if r["kind"] == "stated_fact"]
    assert typed and typed[0]["produced_by"]["step"] == "typed by the submitter"


def test_extracted_findings_from_a_model_step_are_not_credited_to_the_model():
    # The geolocation job ran the vision model and also looked GPS up in OpenStreetMap; the first real
    # package credited the OpenStreetMap place name to the model.
    import uuid
    from types import SimpleNamespace as N

    from icclex.package import _ai_provenance

    job = N(id=uuid.uuid4(), agent="geolocation", model="vision-m")
    ev = uuid.uuid4()
    mk = lambda kind, source: N(id=uuid.uuid4(), evidence_id=ev, job_id=job.id, kind=kind, source=source, value={},  # noqa: E731
                                status="confirmed", supersedes_id=None, confirmed_at=None)
    fs = [mk("place", "extracted"), mk("place_candidate", "inferred")]
    prov = _ai_provenance(N(external_processing_consent=True), {ev: "E1"}, {f.id: f for f in fs}, {job.id: job},
                          N(narrative=N(model=None, version=1), dropped=[]))
    by_kind = {r["kind"]: r["produced_by"] for r in prov["findings"]}
    assert by_kind["place"] == {"type": "deterministic", "step": "geolocation", "model": None}
    assert by_kind["place_candidate"]["model"] == "vision-m"


def test_the_filing_assistant_reads_the_same_field_text_the_package_holds(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    build(client, case)
    case_id, headers = case
    o = client.get(f"/api/cases/{case_id}/package/otplink", headers=headers).json()
    z = open_zip(client, case)
    assert o == json.loads(z.read("otplink_fields.json"))
    md = z.read("otplink_fields.md").decode()
    assert [f["field"] for f in o["fields"]][2:4] == ["Incident Name", "Factual Summary"]
    assert all(f["value"] in md for f in o["fields"] if f["value"]) and o["attachments"][0]["label"] == "E1"


def test_a_package_needs_consent_to_send_the_files_as_they_are(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    r = build(client, case, consent=False)
    assert r.status_code == 409 and "as they are" in r.json()["detail"]
    assert build(client, case).status_code == 200
    case_id, headers = case
    events = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"]
    assert any(e["event_type"] == "package_built" and e["detail"]["files_sent_as_they_are"] for e in events)


def test_the_summary_leaves_out_file_details_and_includes_where_a_file_came_from(client, case, run_jobs):
    res, _ = prepared_case(client, case, run_jobs)
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/facts", headers=headers,
                    json={"text": "I received this photo from a neighbour on WhatsApp.", "evidence_id": res["evidence_id"]})
    assert r.status_code == 201 and r.json()["evidence_id"] == res["evidence_id"]
    assert client.post(f"/api/cases/{case_id}/facts", headers=headers,
                       json={"text": "x", "evidence_id": "not-a-uuid"}).status_code == 404
    build(client, case)
    summary = client.get(f"/api/cases/{case_id}/package/otplink", headers=headers).json()["fields"][3]["value"]
    assert "from a neighbour" in summary
    assert "64" not in summary and "JPEG" not in summary  # the 64x48 JPEG's file properties stay out


def test_a_package_needs_the_date_and_place_otplink_requires(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    case_id, headers = case
    client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_location_text": None})
    r = build(client, case)
    assert r.status_code == 409 and "date and place" in r.json()["detail"]
