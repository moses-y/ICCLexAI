"""Fixture files are built in code so the expected values are visible next to the tests."""

import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

# Nairobi, as degrees/minutes/seconds the way EXIF stores them.
NAIROBI = {"lat": -(1 + 17 / 60 + 11 / 3600), "lon": 36 + 49 / 60 + 2 / 3600}
MOMBASA = {"lat": -4.0435, "lon": 39.6682}


def jpeg(*, gps=((1, 17, 11), "S", (36, 49, 2), "E"), taken="2025:06:15 10:30:00", offset="+03:00",
         make="TestCam", model="T1", software=None, color=(200, 30, 30), size=(64, 48), exif=True) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    if not exif:
        img.save(buf, "JPEG")
        return buf.getvalue()
    e = Image.Exif()
    if gps:
        g = e.get_ifd(0x8825)
        g[1], g[2], g[3], g[4] = gps[1], tuple(float(x) for x in gps[0]), gps[3], tuple(float(x) for x in gps[2])
    if taken:
        e.get_ifd(0x8769)[0x9003] = taken
        if offset:
            e.get_ifd(0x8769)[0x9011] = offset
    if make:
        e[0x010F] = make
    if model:
        e[0x0110] = model
    if software:
        e[0x0131] = software
    img.save(buf, "JPEG", exif=e)
    return buf.getvalue()


def png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (10, 120, 10)).save(buf, "PNG")
    return buf.getvalue()


def mp4(*, with_audio=True) -> bytes:
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=duration=2:size=160x120:rate=10"]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-shortest"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "t.mp4"
        subprocess.run([*cmd, "-metadata", "creation_time=2025-06-15T10:30:00Z", "-metadata", "location=+01.2860+036.8170/",
                        "-movflags", "use_metadata_tags", str(out)], check=True)
        return out.read_bytes()


def pdf(title="Report") -> bytes:
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.setTitle(title)
    c.drawString(72, 750, "Witness statement, 15 June 2025, Nairobi.")
    c.save()
    return buf.getvalue()


def have_ffmpeg() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def upload(client, case, name, data, content_type="application/octet-stream"):
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/evidence", headers=headers, files={"files": (name, data, content_type)})
    assert r.status_code == 201, r.text
    return r.json()["results"][0]


def findings(client, case, evidence_id=None):
    case_id, headers = case
    url = f"/api/cases/{case_id}/findings" + (f"?evidence_id={evidence_id}" if evidence_id else "")
    return client.get(url, headers=headers).json()["findings"]


def jobs_by_agent(client, case, evidence_id):
    case_id, headers = case
    ev = next(e for e in client.get(f"/api/cases/{case_id}", headers=headers).json()["evidence"] if e["id"] == evidence_id)
    return {j["agent"]: j for j in ev["jobs"]}
