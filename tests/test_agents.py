import pytest

from icclex import config, worker
from icclex.agents import REGISTRY, llm
from icclex.agents.metadata import dms_to_decimal, parse_iso6709

from .fixtures import MOMBASA, NAIROBI, findings, have_ffmpeg, jobs_by_agent, jpeg, mp4, pdf, upload


def kinds(fs, kind):
    return [f for f in fs if f["kind"] == kind]


def test_gps_time_and_device_are_extracted_from_exif(client, case, run_jobs):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])

    (gps,) = kinds(fs, "gps")
    assert gps["value"]["lat"] == pytest.approx(NAIROBI["lat"], abs=1e-5)
    assert gps["value"]["lon"] == pytest.approx(NAIROBI["lon"], abs=1e-5)
    assert gps["source"] == "extracted" and gps["confidence"] is None
    assert gps["location"]["lat"] == pytest.approx(NAIROBI["lat"], abs=1e-5)  # stored as a PostGIS point

    (taken,) = kinds(fs, "capture_time")
    assert taken["value"]["iso"] == "2025-06-15T10:30:00+03:00" and taken["value"]["tz_known"] is True
    assert kinds(fs, "device")[0]["value"]["make"] == "TestCam"
    assert all(f["status"] == "proposed" for f in fs)  # nothing is confirmed until the submitter says so


def test_a_point_on_the_equator_is_not_discarded(client, case, run_jobs):
    # The old converter tested `if lat and lon`, which drops any coordinate that is exactly 0.0.
    res = upload(client, case, "eq.jpg", jpeg(gps=((0, 0, 0), "N", (36, 0, 0), "E")), "image/jpeg")
    run_jobs()
    (gps,) = kinds(findings(client, case, res["evidence_id"]), "gps")
    assert gps["value"]["lat"] == 0.0 and gps["value"]["lon"] == 36.0


def test_gps_zero_zero_is_ignored_and_flagged(client, case, run_jobs):
    res = upload(client, case, "z.jpg", jpeg(gps=((0, 0, 0), "N", (0, 0, 0), "E")), "image/jpeg")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])
    assert not kinds(fs, "gps")
    assert any(f["value"]["code"] == "gps_zero_zero" for f in kinds(fs, "integrity_flag"))


def test_no_gps_means_no_gps_finding_and_no_invented_location(client, case, run_jobs):
    res = upload(client, case, "n.jpg", jpeg(gps=None), "image/jpeg")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])
    assert not kinds(fs, "gps") and not kinds(fs, "place") and not kinds(fs, "place_candidate")
    note = jobs_by_agent(client, case, res["evidence_id"])["geolocation"]["error"] or ""
    assert "location clues not analysed" in note and "not agreed" in note  # says why there is no location


def test_agents_that_send_data_out_do_not_run_without_consent(client, case, run_jobs, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("an external service was called without consent")

    monkeypatch.setattr(llm, "_client", boom)
    monkeypatch.setattr("icclex.agents.geolocation.reverse_geocode", boom)
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()

    jobs = jobs_by_agent(client, case, res["evidence_id"])
    assert jobs["visual"]["status"] == "failed" and "not agreed" in jobs["visual"]["error"]
    assert jobs["metadata"]["status"] == "done" and jobs["integrity"]["status"] == "done"
    fs = findings(client, case, res["evidence_id"])
    assert not kinds(fs, "description") and not kinds(fs, "place")
    assert "place name" in jobs["geolocation"]["error"]  # said so, rather than leaving a silent gap


def test_with_consent_but_no_model_the_file_is_not_analysed_and_nothing_is_invented(client, case, run_jobs):
    case_id, headers = case
    client.patch(f"/api/cases/{case_id}", headers=headers, json={"external_processing_consent": True})
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    visual = jobs_by_agent(client, case, res["evidence_id"])["visual"]
    assert visual["status"] == "failed" and "not set" in visual["error"]
    assert not kinds(findings(client, case, res["evidence_id"]), "description")


def test_vision_model_must_be_configured_explicitly(monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "x")
    monkeypatch.setattr(config, "VISION_MODEL", None)
    with pytest.raises(Exception, match="ICCLEX_VISION_MODEL"):
        llm.vision_json("s", "p", [(b"img", "image/jpeg")])


@pytest.mark.parametrize("stated, expect_conflict", [
    ((MOMBASA["lat"], MOMBASA["lon"]), True),  # about 440 km from where the file's GPS says
    ((NAIROBI["lat"] + 0.01, NAIROBI["lon"]), False),  # about 1 km away
])
def test_gps_far_from_the_stated_place_is_flagged_and_near_is_not(client, case, run_jobs, stated, expect_conflict):
    case_id, headers = case
    client.patch(f"/api/cases/{case_id}", headers=headers, json={"incident_lat": stated[0], "incident_lon": stated[1]})
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    conflicts = kinds(findings(client, case, res["evidence_id"]), "geo_conflict")
    assert bool(conflicts) is expect_conflict
    if expect_conflict:
        assert 400 < conflicts[0]["value"]["distance_km"] < 500


def test_editing_software_is_a_flag_with_no_verdict(client, case, run_jobs):
    res = upload(client, case, "edited.jpg", jpeg(software="Adobe Photoshop 25.0"), "image/jpeg")
    run_jobs()
    flag = next(f for f in kinds(findings(client, case, res["evidence_id"]), "integrity_flag")
                if f["value"]["code"] == "editing_software")
    assert "not a finding of tampering" in flag["value"]["note"]
    assert flag["source"] == "extracted"


def test_stripped_jpeg_without_exif_is_noted_as_common_not_suspicious(client, case, run_jobs):
    res = upload(client, case, "plain.jpg", jpeg(exif=False), "image/jpeg")
    run_jobs()
    flag = next(f for f in kinds(findings(client, case, res["evidence_id"]), "integrity_flag") if f["value"]["code"] == "no_exif")
    assert flag["value"]["severity"] == "info"


@pytest.mark.skipif(not have_ffmpeg(), reason="ffmpeg is required for the video fixtures")
def test_video_metadata_time_and_location_including_ffmpeg_doubled_tag(client, case, run_jobs):
    res = upload(client, case, "clip.mp4", mp4(), "video/mp4")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])
    (taken,) = kinds(fs, "capture_time")
    assert taken["value"]["iso"] == "2025-06-15T10:30:00.000000Z" and ";" not in taken["value"]["iso"]
    (gps,) = kinds(fs, "gps")
    assert gps["value"]["lat"] == pytest.approx(1.286) and gps["value"]["lon"] == pytest.approx(36.817)
    props = kinds(fs, "file_properties")[0]["value"]
    assert props["duration_s"] == pytest.approx(2.0, abs=0.3)
    jobs = jobs_by_agent(client, case, res["evidence_id"])
    assert jobs["audio_video"]["status"] == "failed" and "not agreed" in jobs["audio_video"]["error"]


@pytest.mark.skipif(not have_ffmpeg(), reason="ffmpeg is required for the video fixtures")
def test_keyframes_are_real_images():
    import tempfile
    from pathlib import Path

    from icclex.agents.frames import extract_keyframes

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "c.mp4"
        p.write_bytes(mp4())
        frames = extract_keyframes(p, 6)
    assert len(frames) == 6 and all(jpg[:3] == b"\xff\xd8\xff" for _, jpg in frames)
    assert [t for t, _ in frames] == sorted(t for t, _ in frames)


def test_pdf_metadata_and_document_agent_needs_consent(client, case, run_jobs):
    res = upload(client, case, "statement.pdf", pdf(), "application/pdf")
    run_jobs()
    fs = findings(client, case, res["evidence_id"])
    assert kinds(fs, "file_properties")[0]["value"]["pages"] == 1
    assert jobs_by_agent(client, case, res["evidence_id"])["document"]["status"] == "failed"


def test_a_crashing_agent_is_retried_then_fails_loudly(client, case, run_jobs, monkeypatch):
    def broken(ctx):
        raise RuntimeError("corrupt file")

    monkeypatch.setitem(REGISTRY, "metadata", broken)
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    meta = jobs_by_agent(client, case, res["evidence_id"])["metadata"]
    assert meta["status"] == "failed" and "RuntimeError: corrupt file" in meta["error"]
    case_id, headers = case
    events = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"]
    assert any(e["event_type"] == "analysis_failed" and e["actor_ref"] == "metadata" for e in events)
    # And the dependents still ran rather than hanging behind the failed job:
    assert jobs_by_agent(client, case, res["evidence_id"])["integrity"]["status"] == "done"


def test_case_moves_to_review_when_all_analysis_has_settled(client, case, run_jobs):
    upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    case_id, headers = case
    assert client.get(f"/api/cases/{case_id}", headers=headers).json()["status"] == "analysing"
    run_jobs()
    assert client.get(f"/api/cases/{case_id}", headers=headers).json()["status"] == "review"


def test_helpers():
    assert dms_to_decimal([_R(1, 1), _R(30, 1), _R(0, 1)], "S") == -1.5
    assert dms_to_decimal([_R(1, 0), _R(0, 1), _R(0, 1)], "N") is None  # zero denominator
    assert parse_iso6709("+01.2860+036.8170+1650.0/") == (1.286, 36.817)
    assert parse_iso6709("+91.0+000.0/") is None
    assert worker  # imported for the fixtures above


class _R:
    def __init__(self, num, den):
        self.num, self.den = num, den


def test_video_frames_are_sent_in_batches_the_vision_model_accepts(monkeypatch):
    from icclex.agents import visual
    from icclex.agents.base import AgentContext

    sizes = []
    monkeypatch.setattr(visual, "require_consent", lambda ctx: None)
    monkeypatch.setattr(visual, "extract_keyframes", lambda path, n: [(float(t), b"jpg") for t in range(n)])
    monkeypatch.setattr(visual, "vision_json", lambda s, p, imgs: (sizes.append(len(imgs)) or {"description": "x"}, "m"))
    ctx = AgentContext.__new__(AgentContext)
    ctx.mime, ctx.path = "video/mp4", None
    visual.run(ctx)
    assert sizes and max(sizes) <= config.VISION_MAX_IMAGES and sum(sizes) == config.KEYFRAME_COUNT


def test_too_many_images_in_one_vision_call_is_a_bug_not_a_model_outage(monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "x")
    monkeypatch.setattr(config, "VISION_MODEL", "m")
    with pytest.raises(ValueError):
        llm.vision_json("s", "p", [(b"img", "image/jpeg")] * (config.VISION_MAX_IMAGES + 1))


def test_a_network_error_is_retried_later_not_failed_for_good(client, case, run_jobs, monkeypatch):
    from icclex.agents.base import AgentTransient

    def offline(ctx):
        raise AgentTransient("vision model call failed: Connection error.")

    monkeypatch.setitem(REGISTRY, "metadata", offline)
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    meta = jobs_by_agent(client, case, res["evidence_id"])["metadata"]
    assert meta["status"] == "queued"  # waiting out JOB_RETRY_DELAYS_S, not claimed again straight away
    case_id, headers = case
    assert client.get(f"/api/cases/{case_id}", headers=headers).json()["status"] == "analysing"


def test_a_failed_step_can_be_rerun_and_the_rerun_is_in_the_custody_log(client, case, run_jobs, monkeypatch):
    calls = []

    def flaky(ctx):
        calls.append(1)
        if len(calls) <= config.JOB_MAX_ATTEMPTS:
            raise RuntimeError("corrupt file")
        return REGISTRY_ORIGINAL["metadata"](ctx)

    REGISTRY_ORIGINAL = dict(REGISTRY)
    monkeypatch.setitem(REGISTRY, "metadata", flaky)
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    case_id, headers = case
    eid = res["evidence_id"]
    assert jobs_by_agent(client, case, eid)["metadata"]["status"] == "failed"

    r = client.post(f"/api/cases/{case_id}/evidence/{eid}/rerun", headers=headers)
    assert r.status_code == 200 and "metadata" in r.json()["requeued"]
    run_jobs()
    assert jobs_by_agent(client, case, eid)["metadata"]["status"] == "done"
    assert kinds(findings(client, case, eid), "gps")
    events = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"]
    assert any(e["event_type"] == "reanalysis_requested" for e in events)
    # Nothing left to re-run is a conflict, not a silent no-op (visual still fails here: no key in tests):
    monkeypatch.setitem(REGISTRY, "visual", lambda ctx: REGISTRY_ORIGINAL["integrity"](ctx))
    client.post(f"/api/cases/{case_id}/evidence/{eid}/rerun", headers=headers)
    run_jobs()
    assert client.post(f"/api/cases/{case_id}/evidence/{eid}/rerun", headers=headers).status_code == 409


def _whisper(language, text, logprob, duration=4):
    return {"text": text, "language": language, "duration": duration,
            "segments": [{"start": 0, "end": 4, "text": text, "avg_logprob": logprob}]}


@pytest.mark.parametrize("passes, expected", [
    # Measured on 2026-11-06: a Nairobi clip came back as Spanish, and forced to Swahili as repeated filler.
    ({None: ("Spanish", "¡Adiós!", -1.15), "en": ("English", "Police", -1.45), "sw": ("Swahili", "Kikisha", -0.66)}, None),
    ({None: ("English", "The police arrived.", -0.13)}, "The police arrived."),
    # A real Nairobi clip forced to Swahili gave one confident word, "Muzika", for 10.5 s of audio.
    ({None: ("Indonesian", "Terima kasih.", -0.36), "en": ("English", "So", -1.36),
      "sw": ("Swahili (macrolanguage)", "Muzika", -0.31, 10.45)}, None),
    # Noisy Swahili was detected as Greek; forcing Swahili recovered it.
    ({None: ("Modern Greek", "Πολίσι", -0.65), "en": ("English", "Police", -1.69),
      "sw": ("Swahili (macrolanguage)", "Polisi walifika sokoni.", -0.31)}, "Polisi walifika sokoni."),
])
def test_a_transcript_is_kept_only_in_an_expected_language_with_enough_confidence(monkeypatch, tmp_path, passes, expected):
    from icclex.agents import audio_video

    monkeypatch.setattr(audio_video, "transcribe", lambda path, name, language=None: (_whisper(*passes[language]), "w"))
    result, _, tried = audio_video._trusted_transcript(tmp_path / "a.mp3")
    assert (result["text"] if result else None) == expected
    assert tried[0].startswith("auto-detected")


def test_a_finished_step_can_be_reanalysed_and_its_old_findings_are_superseded_not_deleted(client, case, run_jobs):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    run_jobs()
    case_id, headers = case
    eid = res["evidence_id"]
    gps_before = kinds(findings(client, case, eid), "gps")[0]
    client.post(f"/api/cases/{case_id}/findings/bulk", headers=headers, json={"ids": [gps_before["id"]], "action": "confirm"})

    r = client.post(f"/api/cases/{case_id}/evidence/{eid}/rerun", headers=headers, json={"agents": ["metadata"]})
    assert r.status_code == 200 and "metadata" in r.json()["requeued"]
    assert gps_before["id"] in r.json()["superseded_findings"]
    run_jobs()
    gps = {f["id"]: f["status"] for f in kinds(findings(client, case, eid), "gps")}
    assert gps_before["id"] not in gps and list(gps.values()) == ["proposed"]  # the listing hides superseded rows
    from icclex.db import session_scope
    from icclex.models import Finding

    with session_scope() as s:  # the old row is kept, only its status changed
        assert s.get(Finding, __import__("uuid").UUID(gps_before["id"])).status == "superseded"
    events = client.get(f"/api/cases/{case_id}/custody", headers=headers).json()["events"]
    assert any(e["event_type"] == "reanalysis_requested" and gps_before["id"] in e["detail"]["superseded_findings"]
               for e in events)


def test_naming_an_unknown_step_to_reanalyse_is_rejected(client, case, run_jobs):
    res = upload(client, case, "a.jpg", jpeg(), "image/jpeg")
    case_id, headers = case
    r = client.post(f"/api/cases/{case_id}/evidence/{res['evidence_id']}/rerun", headers=headers, json={"agents": ["bogus"]})
    assert r.status_code == 422
