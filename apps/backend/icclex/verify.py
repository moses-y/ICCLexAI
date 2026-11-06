"""Re-hash every stored original and record the result in the custody log. A mismatch means the file on
disk is no longer what was uploaded (disk fault, or someone changed it); the log entry is the evidence."""

import logging
import time

from sqlalchemy import select

from . import config, custody
from .db import session_scope
from .models import Evidence
from .storage import LocalStorage, get_storage

log = logging.getLogger("icclex.verify")


def verify_originals(storage: LocalStorage | None = None) -> dict[str, int]:
    """Returns counts: ok, mismatch, missing. One transaction per file, so a long run keeps progress."""
    storage = storage or get_storage()
    with session_scope() as s:
        ids = s.execute(select(Evidence.id)).scalars().all()
    counts = {"ok": 0, "mismatch": 0, "missing": 0}
    for evidence_id in ids:
        with session_scope() as s:
            ev = s.get(Evidence, evidence_id)
            try:
                actual = storage.sha256_of(ev.storage_uri)
            except FileNotFoundError:
                actual = None
            if actual == ev.sha256:
                outcome, event = "ok", "hash_verified"
            else:
                outcome, event = ("missing" if actual is None else "mismatch"), "hash_mismatch"
                log.error("evidence %s: stored hash %s, found %s", ev.id, ev.sha256, actual or "file missing")
            counts[outcome] += 1
            custody.record(s, ev.case_id, event, actor_type="system", actor_ref="verify", evidence_id=ev.id,
                           detail={"expected_sha256": ev.sha256, "actual_sha256": actual})
    return counts


class DailyVerifier:
    """Run from the worker loop: verifies at most once per VERIFY_INTERVAL_S."""

    def __init__(self):
        self.last = 0.0

    def tick(self) -> None:
        if time.monotonic() - self.last >= config.VERIFY_INTERVAL_S:
            self.last = time.monotonic()
            log.info("hash verification: %s", verify_originals())
