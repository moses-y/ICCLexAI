"""The whole path through the API: upload, analyse, confirm, build the package, check what is in it."""

import csv
import hashlib
import io
import json
import zipfile

import exifread

from icclex import narrative

from .fixtures import findings, jpeg, png, upload


def confirm_all(client, case, evidence_id=None):
    case_id, headers = case
    ids = [f["id"] for f in findings(client, case, evidence_id) if f["status"] == "proposed"]
    r = client.post(f"/api/cases/{case_id}/findings/bulk", headers=headers, json={"ids": ids, "action": "confirm"})
    assert r.status_code == 200 and r.json()["changed"] == len(ids)
    return ids


def build(client, case, strip=False):
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/package", headers=headers, json={"strip_metadata": strip})
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
    return res, data


def test_package_contains_the_originals_and_a_manifest_that_matches_them(client, case, run_jobs):
    res, data = prepared_case(client, case, run_jobs)
    r = build(client, case)
    assert r.status_code == 200, r.text

    z = open_zip(client, case)
    names = set(z.namelist())
    assert {"README_FIRST.txt", "manifest.json", "manifest.csv", "summary.pdf", "evidence_map.geojson", "custody_log.csv",
            "otplink_fields.md"} <= names
    manifest = json.loads(z.read("manifest.json"))
    (row,) = manifest["evidence"]
    assert row["sha256_original"] == hashlib.sha256(data).hexdigest() == res["sha256"]
    assert z.read(row["file_in_package"]) == data and row["metadata_removed"] is False
    assert hashlib.sha256(z.read("manifest.json")).hexdigest() == r.json()["manifest_sha256"]
    assert manifest["custody_chain_valid"] is True
    assert z.read("summary.pdf")[:5] == b"%PDF-"
    rows = list(csv.DictReader(io.StringIO(z.read("manifest.csv").decode())))
    assert rows[0]["sha256_original"] == res["sha256"]


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

        citable = s.query(Finding).filter(Finding.status.in_(("confirmed", "edited"))).count()
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

    dev = next(f for f in findings(client, case) if f["kind"] == "device")
    edited = client.patch(f"/api/cases/{case_id}/findings/{dev['id']}", headers=headers,
                          json={"action": "edit", "value": {**dev["value"], "make": "Corrected Make"}})
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
        assert current.version == 2 and "The submitter wrote: recording device details: make Corrected Make" in current.body
        assert "TestCam" not in current.body


def test_an_edit_must_keep_the_findings_fields(client, case, run_jobs):
    prepared_case(client, case, run_jobs)
    case_id, headers = case
    dev = next(f for f in findings(client, case) if f["kind"] == "device")
    r = client.patch(f"/api/cases/{case_id}/findings/{dev['id']}", headers=headers, json={"action": "edit", "value": {"make": "x"}})
    assert r.status_code == 422


def test_metadata_stripping_is_lossless_recorded_and_leaves_the_original_alone(client, case, run_jobs):
    res, data = prepared_case(client, case, run_jobs)
    r = build(client, case, strip=True)
    assert r.status_code == 200
    z = open_zip(client, case)
    (row,) = json.loads(z.read("manifest.json"))["evidence"]
    stripped = z.read(row["file_in_package"])

    assert row["metadata_removed"] is True and row["sha256_original"] == hashlib.sha256(data).hexdigest()
    assert row["sha256_in_package"] == hashlib.sha256(stripped).hexdigest() != row["sha256_original"]
    tags = exifread.process_file(io.BytesIO(stripped), details=False)
    assert not [t for t in tags if t.startswith(("GPS", "EXIF")) or t.startswith("Image Make")]
    from PIL import Image

    assert list(Image.open(io.BytesIO(stripped)).getdata()) == list(Image.open(io.BytesIO(data)).getdata())  # same pixels
    # the stored original is untouched, and the export is in the custody log
    assert hashlib.sha256(next((__import__("icclex.config", fromlist=["x"]).STORAGE_ROOT / case[0] / "originals").rglob("photo.jpg")).read_bytes()).hexdigest() == res["sha256"]
    case_id, headers = case
    events = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"]
    assert any(e["event_type"] == "exported" and e["detail"]["metadata_removed"] for e in events)


def test_stripping_a_type_it_cannot_strip_losslessly_is_reported_not_faked(client, case, run_jobs):
    upload(client, case, "p.png", png(), "image/png")
    upload(client, case, "doc.txt", b"a plain text note", "text/plain")
    run_jobs()
    confirm_all(client, case)
    r = build(client, case, strip=True).json()
    z = open_zip(client, case)
    rows = {x["original_name"]: x for x in json.loads(z.read("manifest.json"))["evidence"]}
    assert rows["p.png"]["metadata_removed"] is True and rows["doc.txt"]["metadata_removed"] is False
    assert not any("metadata removal" in d["text"] for d in r["removed_from_draft"])


def test_asking_to_strip_when_nothing_can_be_stripped_says_so(client, case, run_jobs):
    upload(client, case, "doc.txt", b"a plain text note", "text/plain")
    run_jobs()
    confirm_all(client, case)
    r = build(client, case, strip=True).json()
    assert any("metadata removal" in d["text"] and "JPEG or PNG" in d["reason"] for d in r["removed_from_draft"])


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
