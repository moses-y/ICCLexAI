import hashlib
import os
import stat
import uuid

from icclex import config
from icclex.sniff import sniff_mime

from .fixtures import jpeg, png, upload


def test_original_is_stored_untouched_hashed_and_read_only(client, case):
    data = jpeg()
    res = upload(client, case, "evidence.jpg", data, "image/jpeg")

    assert res["sha256"] == hashlib.sha256(data).hexdigest()
    stored = next((config.STORAGE_ROOT / case[0] / "originals").rglob("evidence.jpg"))
    assert stored.read_bytes() == data  # the live path used to replace binary files with "[Binary file: x]"
    assert not stored.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)


def test_type_comes_from_the_bytes_not_the_filename_or_content_type(client, case, run_jobs):
    res = upload(client, case, "holiday.png", jpeg(), "image/png")
    assert res["mime"] == "image/jpeg"
    run_jobs()
    flags = [f for f in __import__("tests.fixtures", fromlist=["findings"]).findings(client, case, res["evidence_id"])
             if f["kind"] == "integrity_flag"]
    assert any(f["value"]["code"] == "extension_mismatch" for f in flags)


def test_the_same_file_twice_is_rejected_and_stored_once(client, case):
    data = jpeg()
    upload(client, case, "a.jpg", data, "image/jpeg")
    case_id, headers = case
    again = client.post(f"/api/cases/{case_id}/evidence", headers=headers, files={"files": ("copy.jpg", data, "image/jpeg")})
    assert again.json()["results"][0]["code"] == 409
    assert len(client.get(f"/api/cases/{case_id}", headers=headers).json()["evidence"]) == 1
    assert len(list((config.STORAGE_ROOT / case_id / "originals").rglob("*.jpg"))) == 1


def test_empty_upload_is_refused(client, case):
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/evidence", headers=headers, files={"files": ("e.jpg", b"", "image/jpeg")})
    assert r.json()["results"][0]["code"] == 400


def test_oversized_upload_is_refused_and_leaves_no_file(client, case, monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 1000)
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/evidence", headers=headers, files={"files": ("big.jpg", b"\xff\xd8\xff" + b"0" * 5000, "image/jpeg")})
    assert r.json()["results"][0]["code"] == 413
    assert not list((config.STORAGE_ROOT / case_id).rglob("big.jpg*"))


def test_hostile_filename_cannot_escape_the_case_directory(client, case):
    upload(client, case, "../../../../tmp/pwned.jpg", jpeg(), "image/jpeg")
    case_id = case[0]
    assert not os.path.exists("/tmp/pwned.jpg")
    assert list((config.STORAGE_ROOT / case_id / "originals").rglob("pwned.jpg"))


def test_upload_writes_a_custody_event_and_queues_jobs(client, case):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    case_id, headers = case
    custody = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()
    received = [e for e in custody["events"] if e["event_type"] == "received"]
    assert received and received[0]["detail"]["sha256"] == res["sha256"]
    assert custody["chain_valid"]
    jobs = client.get(f"/api/cases/{case_id}", headers=headers).json()["evidence"][0]["jobs"]
    assert {j["agent"] for j in jobs} == {"metadata", "geolocation", "visual", "integrity"}
    assert all(j["status"] == "queued" for j in jobs)


def test_sniffing():
    assert sniff_mime(jpeg()[:100]) == "image/jpeg"
    assert sniff_mime(png()[:100]) == "image/png"
    assert sniff_mime(b"%PDF-1.7 ...") == "application/pdf"
    assert sniff_mime(b"plain words") == "text/plain"
    assert sniff_mime(b"\x00\x01\x02\x03\xfe\xff") == "application/octet-stream"
    assert sniff_mime(b"\x00\x00\x00\x18ftypisom") == "video/mp4"
    assert uuid.UUID(int=0)  # keep the import honest
