"""Originals are written once, hashed while they stream in, and made read-only.

On 2026-11-05 the live upload path wrote each file to /tmp, replaced binary content with the string
"[Binary file: name]", and deleted the only copy after analysis. Nothing here ever rewrites a stored
original; derived files are separate artefacts."""

import hashlib
import os
import re
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from . import config


class UploadTooLarge(Exception):
    pass


@dataclass(frozen=True)
class StoredFile:
    storage_uri: str  # relative to the storage root
    sha256: str
    size_bytes: int


_UNSAFE = re.compile(r"[^A-Za-z0-9._ -]")


def safe_name(name: str) -> str:
    """Basename only, no control characters or path separators. The display name is kept in the
    database; this is just what the file is called on disk."""
    base = os.path.basename(name.replace("\\", "/")).strip() or "unnamed"
    cleaned = _UNSAFE.sub("_", base).lstrip(".") or "unnamed"
    return cleaned[:150]


class LocalStorage:
    """Local-disk store. The interface (save_stream, open_path, save_bytes) is all the API and
    agents use, so an S3-compatible store can replace it without touching them."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root or config.STORAGE_ROOT)

    def path(self, storage_uri: str) -> Path:
        full = (self.root / storage_uri).resolve()
        if self.root.resolve() not in full.parents:
            raise ValueError("storage_uri escapes the storage root")
        return full

    def save_stream(self, case_id: uuid.UUID, evidence_id: uuid.UUID, filename: str,
                    chunks: Iterator[bytes], max_bytes: int | None = None) -> StoredFile:
        limit = max_bytes or config.MAX_UPLOAD_BYTES
        uri = f"{case_id}/originals/{evidence_id}/{safe_name(filename)}"
        target = self.path(uri)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".part")
        digest = hashlib.sha256()
        size = 0
        try:
            with open(tmp, "wb") as fh:
                for chunk in chunks:
                    size += len(chunk)
                    if size > limit:
                        raise UploadTooLarge(f"upload exceeds {limit} bytes")
                    digest.update(chunk)
                    fh.write(chunk)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp, 0o444)
            os.replace(tmp, target)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        return StoredFile(uri, digest.hexdigest(), size)

    def save_bytes(self, case_id: uuid.UUID, subdir: str, filename: str, data: bytes) -> StoredFile:
        uri = f"{case_id}/{subdir}/{uuid.uuid4().hex[:8]}_{safe_name(filename)}"
        target = self.path(uri)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        os.chmod(target, 0o444)
        return StoredFile(uri, hashlib.sha256(data).hexdigest(), len(data))

    def save_file(self, case_id: uuid.UUID, subdir: str, filename: str, src: Path) -> StoredFile:
        """Moves a finished file (e.g. the package ZIP, which can be gigabytes) into the store."""
        uri = f"{case_id}/{subdir}/{uuid.uuid4().hex[:8]}_{safe_name(filename)}"
        target = self.path(uri)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest, size = hashlib.sha256(), 0
        with open(src, "rb") as fh:
            for block in iter(lambda: fh.read(config.UPLOAD_CHUNK_BYTES), b""):
                digest.update(block)
                size += len(block)
        os.replace(src, target) if src.stat().st_dev == target.parent.stat().st_dev else target.write_bytes(src.read_bytes())
        os.chmod(target, 0o444)
        return StoredFile(uri, digest.hexdigest(), size)

    def sha256_of(self, storage_uri: str) -> str:
        digest = hashlib.sha256()
        with open(self.path(storage_uri), "rb") as fh:
            for block in iter(lambda: fh.read(config.UPLOAD_CHUNK_BYTES), b""):
                digest.update(block)
        return digest.hexdigest()


def get_storage() -> LocalStorage:
    return LocalStorage()
