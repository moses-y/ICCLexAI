import os

from icclex import config
from icclex.verify import verify_originals

from .fixtures import jpeg, upload


def stored(case_id):
    return next((config.STORAGE_ROOT / case_id / "originals").rglob("*.jpg"))


def events(client, case, kind):
    case_id, headers = case
    return [e for e in client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"] if e["event_type"] == kind]


def test_intact_originals_are_logged_as_verified(client, case):
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    assert verify_originals() == {"ok": 1, "mismatch": 0, "missing": 0}
    (ev,) = events(client, case, "hash_verified")
    assert ev["actor_ref"] == "verify" and ev["detail"]["expected_sha256"] == ev["detail"]["actual_sha256"]


def test_a_changed_original_is_caught_and_logged(client, case):
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    path = stored(case[0])
    os.chmod(path, 0o644)
    path.write_bytes(path.read_bytes() + b"x")  # someone appends a byte
    assert verify_originals() == {"ok": 0, "mismatch": 1, "missing": 0}
    (ev,) = events(client, case, "hash_mismatch")
    assert ev["detail"]["expected_sha256"] != ev["detail"]["actual_sha256"]
    case_id, headers = case
    assert client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["chain_valid"]  # the log itself is intact


def test_a_deleted_original_is_reported_missing(client, case):
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    path = stored(case[0])
    os.chmod(path, 0o644)
    path.unlink()
    assert verify_originals() == {"ok": 0, "mismatch": 0, "missing": 1}
    assert events(client, case, "hash_mismatch")[0]["detail"]["actual_sha256"] is None
