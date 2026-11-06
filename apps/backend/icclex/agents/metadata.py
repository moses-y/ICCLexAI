"""Reads what the file says about itself: capture time, GPS, device, properties. All findings are
source=extracted. Nothing here calls an external service, so it runs without consent."""

import json
import re
import shutil
import subprocess
from datetime import datetime

from .base import AgentContext, AgentResult, AgentUnavailable, FindingDraft


def _ratio(r) -> float | None:
    try:
        num, den = float(r.num), float(r.den)
    except AttributeError:
        try:
            return float(r)
        except (TypeError, ValueError):
            return None
    return None if den == 0 else num / den


def dms_to_decimal(values, ref) -> float | None:
    """EXIF stores degrees, minutes, seconds as three ratios. Compared with `is None`, not truthiness:
    a point on the equator or the prime meridian is 0.0 and valid."""
    try:
        d, m, s = (_ratio(v) for v in values[:3])
    except (TypeError, ValueError):
        return None
    if d is None or m is None or s is None:
        return None
    out = d + m / 60.0 + s / 3600.0
    return -out if str(ref).strip().upper() in ("S", "W") else out


def valid_coords(lat, lon) -> bool:
    return lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180


def parse_iso6709(text: str) -> tuple[float, float] | None:
    """QuickTime/MP4 location atoms, e.g. '+01.2345+036.8123+1650.000/'."""
    m = re.match(r"^([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)", text.strip())
    if not m:
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    return (lat, lon) if valid_coords(lat, lon) else None


def _exif_datetime(raw: str, offset: str | None) -> dict | None:
    try:
        dt = datetime.strptime(raw.strip(), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None
    iso = dt.isoformat()
    tz_known = False
    if offset and re.fullmatch(r"[+-]\d{2}:\d{2}", offset.strip()):
        iso += offset.strip()
        tz_known = True
    return {"iso": iso, "tz_known": tz_known, "raw": raw.strip()}


def _gps_finding(lat: float, lon: float, field: str, altitude: float | None = None) -> FindingDraft:
    value = {"lat": lat, "lon": lon, "field": field}
    if altitude is not None:
        value["altitude_m"] = altitude
    return FindingDraft("gps", value, "extracted", geom=(lat, lon))


def _image(ctx: AgentContext) -> AgentResult:
    import exifread
    from PIL import Image

    out: list[FindingDraft] = []
    with open(ctx.path, "rb") as fh:
        tags = exifread.process_file(fh, details=False)
    with Image.open(ctx.path) as img:
        out.append(FindingDraft("file_properties", {"width": img.width, "height": img.height,
                                                    "format": img.format, "exif_tags_present": len(tags)}, "extracted"))

    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        lat = dms_to_decimal(tags["GPS GPSLatitude"].values, tags.get("GPS GPSLatitudeRef"))
        lon = dms_to_decimal(tags["GPS GPSLongitude"].values, tags.get("GPS GPSLongitudeRef"))
        if lat == 0.0 and lon == 0.0:
            out.append(FindingDraft("integrity_flag", {
                "code": "gps_zero_zero", "detail": "GPS is 0,0 (a camera with no fix writes this); ignored"}, "extracted"))
        elif valid_coords(lat, lon):
            alt = None
            if "GPS GPSAltitude" in tags:
                alt = _ratio(tags["GPS GPSAltitude"].values[0])
            out.append(_gps_finding(lat, lon, "EXIF GPS", alt))

    for field in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
        if field in tags:
            offset_tag = {"EXIF DateTimeOriginal": "EXIF OffsetTimeOriginal",
                          "EXIF DateTimeDigitized": "EXIF OffsetTimeDigitized",
                          "Image DateTime": "EXIF OffsetTime"}[field]
            parsed = _exif_datetime(str(tags[field]), str(tags[offset_tag]) if offset_tag in tags else None)
            if parsed:
                out.append(FindingDraft("capture_time", {**parsed, "field": field}, "extracted"))
                break

    device = {k: str(tags[t]).strip() for k, t in
              (("make", "Image Make"), ("model", "Image Model"), ("software", "Image Software")) if t in tags}
    if device:
        out.append(FindingDraft("device", device, "extracted"))
    return AgentResult(findings=out)


def _ffprobe(ctx: AgentContext) -> AgentResult:
    if not shutil.which("ffprobe"):
        raise AgentUnavailable("ffprobe is not installed")
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(ctx.path)],
        capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise AgentUnavailable(f"ffprobe could not read the file: {proc.stderr.strip()[:200]}")
    info = json.loads(proc.stdout)
    fmt = info.get("format", {})
    tags = {k.lower(): v for k, v in (fmt.get("tags") or {}).items()}
    out: list[FindingDraft] = []

    props: dict = {"duration_s": float(fmt["duration"]) if "duration" in fmt else None,
                   "container": fmt.get("format_name"), "streams": []}
    for st in info.get("streams", []):
        entry = {"type": st.get("codec_type"), "codec": st.get("codec_name")}
        if st.get("codec_type") == "video":
            entry.update(width=st.get("width"), height=st.get("height"), fps=st.get("avg_frame_rate"))
        props["streams"].append(entry)
    out.append(FindingDraft("file_properties", props, "extracted"))

    # ffmpeg can write "2025-06-15T10:30:00.000000Z;2025-06-15T10:30:00Z" (the tag twice); keep the first.
    created = (tags.get("creation_time") or "").split(";")[0].strip()
    if created:
        out.append(FindingDraft("capture_time", {"iso": created, "tz_known": created.endswith(("Z", "+00:00")),
                                                 "raw": created, "field": "container creation_time"}, "extracted"))
    for key in ("location", "com.apple.quicktime.location.iso6709"):
        if key in tags and (coords := parse_iso6709(tags[key])):
            out.append(_gps_finding(coords[0], coords[1], key))
            break
    device = {k: tags[t] for k, t in (("make", "com.apple.quicktime.make"), ("model", "com.apple.quicktime.model"),
                                      ("software", "com.apple.quicktime.software"), ("encoder", "encoder")) if t in tags}
    if device:
        out.append(FindingDraft("device", device, "extracted"))
    return AgentResult(findings=out)


def _pdf(ctx: AgentContext) -> AgentResult:
    import pymupdf

    with pymupdf.open(ctx.path) as doc:
        meta = {k: v for k, v in (doc.metadata or {}).items() if v}
        pages = doc.page_count
    out = [FindingDraft("file_properties", {"pages": pages, **{k: meta[k] for k in
                                                              ("title", "author", "producer", "creator") if k in meta}}, "extracted")]
    m = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?(\d{2})?", meta.get("creationDate", ""))
    if m:
        parts = [int(g) if g else 0 for g in m.groups()]
        try:
            out.append(FindingDraft("capture_time", {
                "iso": datetime(*parts).isoformat(), "tz_known": False, "raw": meta["creationDate"],
                "field": "PDF creationDate"}, "extracted"))
        except ValueError:
            pass  # a malformed date is not a capture time
    return AgentResult(findings=out)


def _docx(ctx: AgentContext) -> AgentResult:
    from docx import Document

    props = Document(str(ctx.path)).core_properties
    out = [FindingDraft("file_properties", {"author": props.author or None, "last_modified_by": props.last_modified_by or None,
                                            "title": props.title or None}, "extracted")]
    if props.created:
        out.append(FindingDraft("capture_time", {"iso": props.created.isoformat(), "tz_known": props.created.tzinfo is not None,
                                                 "raw": props.created.isoformat(), "field": "DOCX created"}, "extracted"))
    return AgentResult(findings=out)


def run(ctx: AgentContext) -> AgentResult:
    if ctx.mime.startswith("image/"):
        return _image(ctx)
    if ctx.mime.startswith(("video/", "audio/")):
        return _ffprobe(ctx)
    if ctx.mime == "application/pdf":
        return _pdf(ctx)
    if ctx.mime.endswith("wordprocessingml.document"):
        return _docx(ctx)
    if ctx.mime == "text/plain":
        return AgentResult(findings=[FindingDraft("file_properties", {"bytes": ctx.path.stat().st_size}, "extracted")])
    raise AgentUnavailable(f"no metadata reader for {ctx.mime}")
