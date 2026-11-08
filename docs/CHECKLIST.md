# Checklist

Where ICCLexAI stands. Update this when an item changes; give the date and how it was verified.

## Done and verified

- [x] **Case engine on PostgreSQL + PostGIS**: write-once evidence hashes, hash-chained custody log,
      immutable findings, citation-checked narrative. All 83 tests pass against a real Postgres (2026-11-06).
- [x] **Models configured and checked against the Groq account** (2026-11-06): text `openai/gpt-oss-120b`,
      vision `qwen/qwen3.8-27b` (the only vision model on the account), speech `whisper-large-v3-turbo`.
- [x] **Vision calls fit the free tier.** Every vision call failed on the first live run: Groq refused
      2048-token requests against a 1000 output-tokens-per-minute limit, and videos sent 6 frames to a
      model that takes 3. Now capped at 1000 tokens and 3 images per call.
- [x] **Network errors and rate limits retry later** instead of failing for good: re-queued after 60 s,
      then 300 s (migration `0003`). Groq's client also waits out rate limits itself, up to 5 times.
- [x] **Failed steps can be re-run**: `POST /api/cases/{case}/evidence/{evidence}/rerun`, recorded in
      the custody log as `reanalysis_requested`.
- [x] **End-to-end run with real models** (2026-11-06), with consent on: a GPS-tagged photo, a test
      image, a PDF and a short video. Every step finished; the two video steps that failed when the
      network dropped were re-run through the new endpoint and completed.
- [x] **OTPLink fields and limits match the live form** (rendered 2026-11-06): see
      [otplink-field-map.md](otplink-field-map.md). The package warns when a case exceeds them.
- [x] **AI provenance in every package** (2026-11-06): `ai_provenance.json` names, for each included
      finding, whether a model, deterministic code or the submitter produced it, which model, and how a
      person reviewed it; README_FIRST.txt carries an AI-use statement. Checked on the real case.
- [x] **Project tree tidied**: unused apps, tools, shared UI and stale docs moved to `ARCHIVED_REDUNDANT/`.

## Open

- [ ] **Rotate the Groq key** that was once hardcoded in an archived Streamlit app (noted in commit `ebd3abc`).
- [x] **Transcripts are measured, not guessed** (2026-11-06): `evals/transcription/` runs 180 FLEURS clips
      (Swahili and English, clean and noisy, plus 30 with no speech) through the production code. Invented
      transcripts of no-speech clips fell from 57% to 3% with no good transcript lost.
- [ ] **Noisy Swahili is weak**: only 9 of 25 Swahili clips with crowd babble transcribe well. A model
      limit, not invention; consider a Swahili-tuned model. No Sheng or real field recordings in the set yet.
- [ ] **Free-tier speed.** At 1000 output tokens per minute a few files take several minutes. Groq's
      Dev tier would remove the wait; a cost decision.
- [ ] **What OTPLink returns after Submit** (a reference number and its format) is unknown; it needs a
      real submission.
- [ ] **Ask the OTP** whether metadata should be left intact and whether AI-assisted descriptions are
      acceptable.
- [ ] **Chain-of-custody columns**: copy the Eurojust / ICC-OTP 2022 guidelines' annex into `custody_log.csv`.
- [ ] **Prompt version in provenance.** Jobs record the model but not the prompt text used; add a prompt
      hash per job so a finding can be traced to the exact instructions.
- [ ] **Show provenance in the UI** (a model badge on each finding), not only in the package.
- [ ] **Frontend button for re-run.** The endpoint exists; the case UI does not call it yet.
- [ ] **Deployment workflows** in `.github/workflows/` (`deploy.yml`, `deploy-hf.yml`,
      `deploy-netlify.yml`, `deploy-railway.yml`) predate the case engine; `deploy.yml` still refers to
      Streamlit. Review before any deploy.
- [ ] **`streamlit` in `pyproject.toml`** is only needed by archived apps; remove it once nothing uses it.
- [ ] **`libs/icc_automation/`**: old agents kept until the new ones are accepted; archive after that.
- [ ] **GitHub Pages project site**: a public page for the project (what it does, the five steps with
      screenshots, the AI design and the transcript-gate numbers) linked from the README and LinkedIn.
      Static only, built from `docs/`; it must not host the case app, which handles evidence.
- [ ] **CI that runs the tests** on every push, against a PostGIS service container, with a status badge
      in the README. No workflow runs pytest today, so the README carries no test badge.
- [ ] **Pre-fill when and where in step 3** from the person's own account first, then file-name dates
      and the most specific place suggestion, confirmed with one click.
- [ ] **Assisted sending**: a browser on the server fills OTPLink, the person watches live, ticks the
      reCAPTCHA and clicks Submit; the reference is read from the confirmation page. Never solve the
      captcha, never submit for testing.

## Decided

- **No Temporal for now** (2026-11-06). The Postgres job queue already survives crashes and restarts;
  what was missing was delayed retry and re-run, now added. Reconsider if analysis becomes long
  multi-step workflows that wait on people or run for hours.
