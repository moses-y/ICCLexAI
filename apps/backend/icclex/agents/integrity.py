"""Metadata consistency checks. Output is flags, never a verdict: a flag means "look at this", and
every flag carries that wording. This agent does not detect AI-generated or doctored pixels; no check
here can show a file is authentic or fake. Local only, so it runs without consent."""

import os
import re

from ..sniff import EXTENSIONS_BY_MIME
from .base import AgentContext, AgentResult, FindingDraft

NOT_A_VERDICT = "A flag is not a finding of tampering; it is something worth checking."
EDITORS = re.compile(r"photoshop|lightroom|gimp|snapseed|pixelmator|affinity|paint\.net|canva|picsart|facetune|"
                     r"stable diffusion|midjourney|dall-?e|firefly|comfyui", re.I)


def _flag(code: str, detail: str, severity: str = "notice") -> FindingDraft:
    return FindingDraft("integrity_flag", {"code": code, "severity": severity, "detail": detail,
                                           "note": NOT_A_VERDICT}, "extracted")


def _image_flags(ctx: AgentContext) -> list[FindingDraft]:
    import exifread

    with open(ctx.path, "rb") as fh:
        tags = exifread.process_file(fh, details=False)
    flags = []
    exif_tags = [t for t in tags if t.startswith(("EXIF", "GPS")) or t in ("Image Make", "Image Model")]
    if ctx.mime == "image/jpeg" and not exif_tags:
        flags.append(_flag("no_exif", "No camera metadata. Messaging apps and some phones strip it, so this "
                           "is common and says nothing about the content.", "info"))
    software = str(tags.get("Image Software", ""))
    if software and EDITORS.search(software):
        flags.append(_flag("editing_software", f"The metadata names software that edits or generates images: {software}."))
    original, modified = tags.get("EXIF DateTimeOriginal"), tags.get("Image DateTime")
    if original and modified and str(original) != str(modified):
        flags.append(_flag("modified_after_capture", f"Capture time {original} differs from last-modified {modified}.", "info"))
    return flags


def _pdf_flags(ctx: AgentContext) -> list[FindingDraft]:
    import pymupdf

    with pymupdf.open(ctx.path) as doc:
        meta = doc.metadata or {}
    flags = []
    if meta.get("creationDate") and meta.get("modDate") and meta["creationDate"] != meta["modDate"]:
        flags.append(_flag("pdf_modified", f"Created {meta['creationDate']}, modified {meta['modDate']}.", "info"))
    if meta.get("producer") and EDITORS.search(meta["producer"]):
        flags.append(_flag("editing_software", f"PDF producer: {meta['producer']}."))
    return flags


def run(ctx: AgentContext) -> AgentResult:
    flags: list[FindingDraft] = []
    ext = os.path.splitext(ctx.original_name)[1].lower()
    allowed = EXTENSIONS_BY_MIME.get(ctx.mime)
    if allowed and ext not in allowed:
        flags.append(_flag("extension_mismatch",
                           f"The file is named '{ctx.original_name}' but its contents are {ctx.mime}."))
    if ctx.mime.startswith("image/"):
        flags += _image_flags(ctx)
    elif ctx.mime == "application/pdf":
        flags += _pdf_flags(ctx)
    elif ctx.mime.startswith(("video/", "audio/")):
        for f in ctx.prior_findings:
            if f["kind"] == "device" and f["value"].get("encoder") and re.search(r"lavf|handbrake|ffmpeg", f["value"]["encoder"], re.I):
                flags.append(_flag("re_encoded", f"Encoded by {f['value']['encoder']}: the file was re-encoded after "
                                   "recording, so the original recording may be elsewhere.", "info"))
    return AgentResult(findings=flags)
