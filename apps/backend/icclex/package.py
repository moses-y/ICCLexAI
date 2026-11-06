"""Builds the submission package the user files on OTPLink themselves. Nothing here contacts the ICC.

Contents: originals (or metadata-stripped copies when the submitter chose that), manifest with SHA-256
for every file, summary PDF, GeoJSON of confirmed locations, the custody log, and the text to paste
into each OTPLink field. Only confirmed or edited findings go in; unreviewed and rejected ones are
counted and left out, and the PDF says how many."""

import csv
import hashlib
import io
import json
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import custody
from .models import Artefact, Case, CustodyEvent, Evidence, Finding, NarrativeClaim, SubmissionPackage
from .narrative import NarrativeResult, attribute, build_narrative, citable_findings
from .storage import LocalStorage
from .strip import strip_metadata
from .timeline import rebuild_timeline

DISCLAIMER = (
    "Prepared with AI assistance by ICCLexAI. This is a package for the submitter to file; it has not been "
    "submitted to anyone. It is not legal advice and makes no finding that any crime was committed or that "
    "the ICC has jurisdiction. AI-suggested statements are marked and were confirmed by the submitter."
)
OTPLINK_CAVEAT = (
    "The headings below follow the live OTPLink form as rendered on 2026-11-06 (otplink.icc-cpi.int). The form "
    "can change: compare each heading with the live form before pasting."
)
# Limits shown on the live OTPLink form on 2026-11-06. The 2023 reports this tool was first built from only gave
# "about 4 GB", which is the total, not the per-file limit.
OTPLINK_MAX_FILE_BYTES = 2 * 1000**3
OTPLINK_MAX_TOTAL_BYTES = 4 * 1000**3
OTPLINK_MAX_FILES = 1000
OTPLINK_INCIDENT_NAME_MAX_CHARS = 100
OTPLINK_SUMMARY_MAX_BYTES = int(1.8 * 1000**2)


def _otplink_limit_warnings(name: str, summary: str, rows: list[dict]) -> list[str]:
    out = []
    if len(name) > OTPLINK_INCIDENT_NAME_MAX_CHARS:
        out.append(f"Incident name is {len(name)} characters; OTPLink accepts {OTPLINK_INCIDENT_NAME_MAX_CHARS}.")
    if len(summary.encode()) > OTPLINK_SUMMARY_MAX_BYTES:
        out.append("Factual summary is larger than OTPLink's 1.8 MB limit.")
    big = [r["file_in_package"] for r in rows if r["size_bytes"] > OTPLINK_MAX_FILE_BYTES]
    if big:
        out.append("Over OTPLink's 2.0 GB per-file limit: " + ", ".join(big) + ".")
    if sum(r["size_bytes"] for r in rows) > OTPLINK_MAX_TOTAL_BYTES:
        out.append("Files total more than OTPLink's 4.0 GB per submission; split them across submissions.")
    if len(rows) > OTPLINK_MAX_FILES:
        out.append(f"{len(rows)} files; OTPLink accepts {OTPLINK_MAX_FILES} per submission.")
    return out


class PackageError(Exception):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _point(geog) -> tuple[float, float] | None:
    if geog is None:
        return None
    from geoalchemy2.shape import to_shape

    p = to_shape(geog)
    return (p.y, p.x)


def _incident_text(case: Case, timeline) -> tuple[str, str]:
    period = case.incident_period
    if period is not None and period.lower:
        when = period.lower.date().isoformat() + (f" to {period.upper.date().isoformat()}" if period.upper else "")
    else:
        dated = [e for e in timeline if e.occurred_at]
        when = dated[0].occurred_at.date().isoformat() if dated else "not stated"
    return case.incident_name or "(no name given)", when


def _pdf(case, labels, evidence, per_evidence, result: NarrativeResult, timeline, counts, claims_by_sentence) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    body, small = styles["BodyText"], styles["BodyText"].clone("small", fontSize=8, leading=10)
    P = lambda text, style=body: Paragraph(escape(text), style)  # noqa: E731  (all text here is user or model supplied)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                            title=f"Submission package {case.id}")
    story = [P("Information for the ICC Office of the Prosecutor", styles["Title"]), P(DISCLAIMER, small), Spacer(1, 12),
             P(f"Case reference (internal): {case.id}"), P(f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}"),
             P(f"Incident: {case.incident_name or '(no name given)'}")]
    if counts["unreviewed"] or counts["rejected"]:
        story.append(P(f"Left out: {counts['unreviewed']} findings the submitter did not review and {counts['rejected']} "
                       "they rejected.", small))

    story += [Spacer(1, 12), P("Account", styles["Heading2"])]
    seen = set()
    for idx in sorted(claims_by_sentence):
        text, cited = claims_by_sentence[idx]
        refs = sorted({labels.get(f.evidence_id, "S") for f in cited})
        story.append(P(f"{text} [{', '.join(refs)}]"))
        seen.add(idx)
    if result.dropped:
        story.append(P(f"{len(result.dropped)} draft sentence(s) were removed because they had no confirmed source "
                       "or stated a legal conclusion.", small))

    if timeline:
        story += [Spacer(1, 12), P("Timeline", styles["Heading2"])]
        rows = [["When", "Precision", "What"]] + [[e.occurred_at.isoformat(timespec="minutes") if e.occurred_at else "unknown",
                                                   e.time_precision, e.label[:120]] for e in timeline]
        t = Table([[P(c, small) for c in r] for r in rows], colWidths=[4.5 * cm, 2.5 * cm, 10 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, "#999999"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(t)

    for ev in evidence:
        story += [PageBreak(), P(f"{labels[ev.id]}: {ev.original_name}", styles["Heading2"]),
                  P(f"SHA-256 (original): {ev.sha256}", small), P(f"{ev.mime_sniffed}, {ev.size_bytes} bytes, received "
                                                                  f"{ev.received_at.isoformat(timespec='seconds')}", small), Spacer(1, 8)]
        rows = [["Kind", "Source", "Status", "Detail"]]
        for f in per_evidence.get(ev.id, []):
            rows.append([f.kind, f.source, f.status, attribute(f)[:400]])
        if len(rows) == 1:
            rows.append(["", "", "", "No confirmed findings for this file."])
        t = Table([[P(c, small) for c in r] for r in rows], colWidths=[2.6 * cm, 1.9 * cm, 1.9 * cm, 10.6 * cm], repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, "#999999"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(t)
    doc.build(story)
    return buf.getvalue()


def _custody_csv(events: list[CustodyEvent]) -> bytes:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["at", "event_type", "actor_type", "actor_ref", "evidence_id", "detail", "prev_event_hash", "event_hash"])
    for e in sorted(events, key=lambda e: e.at):
        w.writerow([e.at.isoformat(), e.event_type, e.actor_type, e.actor_ref, e.evidence_id or "",
                    json.dumps(e.detail, sort_keys=True), e.prev_event_hash, e.event_hash])
    return out.getvalue().encode()


def build_package(session: Session, case: Case, storage: LocalStorage, *, strip_metadata_on_export: bool,
                  use_model: bool) -> tuple[SubmissionPackage, NarrativeResult]:
    evidence = list(session.execute(select(Evidence).where(Evidence.case_id == case.id)
                                    .order_by(Evidence.received_at, Evidence.original_name)).scalars())
    if not evidence:
        raise PackageError("add at least one file before building a package")
    if any(e.status in ("received", "analysing") for e in evidence):
        raise PackageError("some files are still being analysed")
    if not citable_findings(session, case.id):
        raise PackageError("confirm at least one finding first: the package only contains confirmed findings")

    timeline = rebuild_timeline(session, case.id)
    result = build_narrative(session, case.id, use_model=use_model)
    claims = list(session.execute(select(NarrativeClaim).where(NarrativeClaim.narrative_id == result.narrative.id)
                                  .order_by(NarrativeClaim.sentence_index)).scalars())
    findings_by_id = {f.id: f for f in session.execute(select(Finding).where(Finding.case_id == case.id)).scalars()}
    claims_by_sentence: dict[int, tuple[str, list[Finding]]] = {}
    for c in claims:
        text, cited = claims_by_sentence.setdefault(c.sentence_index, (c.text, []))
        cited.append(findings_by_id[c.finding_id])

    all_findings = list(findings_by_id.values())
    counts = {"unreviewed": sum(f.status == "proposed" for f in all_findings),
              "rejected": sum(f.status == "rejected" for f in all_findings)}
    per_evidence: dict = {}
    for f in all_findings:
        if f.status in ("confirmed", "edited") and f.evidence_id:
            per_evidence.setdefault(f.evidence_id, []).append(f)
    labels = {e.id: f"E{i}" for i, e in enumerate(evidence, start=1)}
    ok_chain, chain_problem = custody.verify_chain(session, case.id)

    manifest_rows, geojson = [], {"type": "FeatureCollection", "features": []}
    with tempfile.TemporaryDirectory() as tmp:
        zpath = Path(tmp) / "package.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
            for e in evidence:
                src = storage.path(e.storage_uri)
                member = f"originals/{labels[e.id]}_{Path(e.storage_uri).name}"
                stripped = False
                if strip_metadata_on_export:
                    data = strip_metadata(src.read_bytes(), e.mime_sniffed)
                    if data is not None:
                        z.writestr(member, data)
                        stripped, packaged_sha = True, _sha(data)
                        stored = storage.save_bytes(case.id, f"derived/{e.id}", f"stripped_{Path(src).name}", data)
                        session.add(Artefact(case_id=case.id, evidence_id=e.id, kind="stripped_copy",
                                             storage_uri=stored.storage_uri, sha256=stored.sha256))
                        custody.record(session, case.id, "exported", actor_type="system", actor_ref="package",
                                       evidence_id=e.id, detail={"metadata_removed": True, "sha256_original": e.sha256,
                                                                 "sha256_exported": packaged_sha})
                if not stripped:
                    z.write(src, member)
                    packaged_sha = e.sha256
                manifest_rows.append({
                    "label": labels[e.id], "evidence_id": str(e.id), "original_name": e.original_name,
                    "mime": e.mime_sniffed, "size_bytes": e.size_bytes, "sha256_original": e.sha256,
                    "file_in_package": member, "metadata_removed": stripped, "sha256_in_package": packaged_sha,
                    "confirmed_findings": len(per_evidence.get(e.id, []))})
                for f in per_evidence.get(e.id, []):
                    if f.kind == "gps":
                        geojson["features"].append({"type": "Feature", "geometry": {
                            "type": "Point", "coordinates": [f.value["lon"], f.value["lat"]]},
                            "properties": {"evidence": labels[e.id], "file": e.original_name, "source": f.source}})
            if strip_metadata_on_export and not any(r["metadata_removed"] for r in manifest_rows):
                result.dropped.append({"text": "(metadata removal)", "reason": "no file in this case is a JPEG or PNG, "
                                       "the only types this tool strips losslessly"})

            events = list(session.execute(select(CustodyEvent).where(CustodyEvent.case_id == case.id)).scalars())
            manifest = {"case_id": str(case.id), "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                        "narrative_version": result.narrative.version, "custody_chain_valid": ok_chain,
                        "custody_chain_problem": chain_problem, "evidence": manifest_rows}
            manifest_json = json.dumps(manifest, indent=2).encode()
            mcsv = io.StringIO()
            w = csv.DictWriter(mcsv, fieldnames=list(manifest_rows[0]))
            w.writeheader()
            w.writerows(manifest_rows)

            name, when = _incident_text(case, timeline)
            loc = _point(case.incident_location)
            limits = _otplink_limit_warnings(name, result.narrative.body, manifest_rows)
            fields = "\n".join([
                "# OTPLink field text", "", f"> {OTPLINK_CAVEAT}", "",
                "## Limits", *(limits or ["Within OTPLink's limits (2.0 GB per file, 4.0 GB and 1000 files per submission)."]), "",
                "## Investigation", "Choose the situation from OTPLink's list; ICCLexAI does not pick it for you.", "",
                "## Contact Name / Contact Email / Contact Phone",
                "Or tick \"I want to make this submission anonymously\". Choose what is safe for you.", "",
                f"## Incident Name (max {OTPLINK_INCIDENT_NAME_MAX_CHARS} characters)", name, "",
                "## Factual Summary", result.narrative.body, "",
                "## Date of Incident (Start Date / End Date)", when, "",
                "## Language of the Item", "Choose the language of the attached material.", "",
                "## Location of Incident", (case.incident_location_text or "(not stated)") +
                (f"\n\nMap pin: {loc[0]:.5f}, {loc[1]:.5f}" if loc else ""), "",
                "## Add Attachment(s), in this order", *[f"{r['label']}. {r['file_in_package']}  (SHA-256 {r['sha256_in_package']})"
                                                       for r in manifest_rows], "",
                "OTPLink asks that you do not use a VPN or proxy while submitting.", "",
                "## Afterwards", "Record any reference OTPLink gives you in ICCLexAI, then mark the case as filed.", ""])
            readme = (f"{DISCLAIMER}\n\nBefore uploading, check each file's SHA-256 against manifest.json "
                      "(sha256sum on Linux and macOS, Get-FileHash on Windows).\n")
            z.writestr("README_FIRST.txt", readme)
            z.writestr("manifest.json", manifest_json)
            z.writestr("manifest.csv", mcsv.getvalue())
            z.writestr("summary.pdf", _pdf(case, labels, evidence, per_evidence, result, timeline, counts, claims_by_sentence))
            z.writestr("evidence_map.geojson", json.dumps(geojson, indent=2))
            z.writestr("custody_log.csv", _custody_csv(events))
            z.writestr("otplink_fields.md", fields)
        stored_zip = storage.save_file(case.id, "packages", f"icclex_package_{str(case.id)[:8]}.zip", zpath)

    for old in session.execute(select(SubmissionPackage).where(SubmissionPackage.case_id == case.id,
                                                               SubmissionPackage.status == "current")).scalars():
        old.status = "stale"
    version = (session.execute(select(SubmissionPackage.version).where(SubmissionPackage.case_id == case.id)
                               .order_by(SubmissionPackage.version.desc()).limit(1)).scalar() or 0) + 1
    art = Artefact(case_id=case.id, kind="package_zip", storage_uri=stored_zip.storage_uri, sha256=stored_zip.sha256)
    session.add(art)
    session.flush()
    pkg = SubmissionPackage(case_id=case.id, narrative_id=result.narrative.id, zip_artefact_id=art.id, version=version,
                            manifest_sha256=_sha(manifest_json), status="current")
    session.add(pkg)
    result.narrative.status = "approved"
    case.status = "package_ready"
    custody.record(session, case.id, "package_built", actor_type="system", actor_ref="package",
                   detail={"version": version, "zip_sha256": stored_zip.sha256, "manifest_sha256": pkg.manifest_sha256,
                           "metadata_removed": strip_metadata_on_export})
    session.flush()
    return pkg, result
