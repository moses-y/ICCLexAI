<div align="center">

# ICCLexAI

**Evidence preparation for the ICC Office of the Prosecutor, with the person in control of every decision.**

[![License: MIT](https://img.shields.io/badge/license-MIT-0F2240.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-0F2240?logo=python&logoColor=white)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-157A84?logo=fastapi&logoColor=white)](apps/backend/icclex/main.py)
[![React](https://img.shields.io/badge/React-18-157A84?logo=react&logoColor=white)](apps/frontend/package.json)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20PostGIS-0F2240?logo=postgresql&logoColor=white)](docker-compose.yml)
[![Files to: ICC OTPLink](https://img.shields.io/badge/files%20to-ICC%20OTPLink-0F2240)](https://otplink.icc-cpi.int)
[![AI: Groq](https://img.shields.io/badge/AI-Groq-F55036)](https://groq.com)
[![Models](https://img.shields.io/badge/models-gpt--oss--120b%20%C2%B7%20Qwen%20%C2%B7%20Whisper-CFA348)](#ai-system-design)
[![Status: pre-release](https://img.shields.io/badge/status-pre--release-CFA348)](#status-and-roadmap)

<sub>An independent project. Not affiliated with or endorsed by the International Criminal Court.</sub>

[Journey](#the-journey-step-by-step) ·
[Architecture](#architecture) ·
[Run it](#running-it) ·
[API](#api) ·
[Privacy](#privacy) ·
[Roadmap](#status-and-roadmap)

</div>

**Turn your own photos, videos, recordings and account into a submission you file yourself with the
International Criminal Court's Office of the Prosecutor (OTP), on its OTPLink portal.**

AI agents read each file: when and where it was captured, what it shows, what is said in it, and
whether its details are consistent. Each agent says how it knows what it reports. You confirm, edit
or reject every finding, and only what you confirm goes into the submission.

![Start screen](docs/screenshots/start.png)

> **What it does not do.** It gives no legal advice. It never says that a crime happened or that the
> ICC has jurisdiction. It never submits anything to the ICC on your behalf. Sending information to the
> OTP does not open a case: the Prosecutor decides what to do with what is received.

---

## Contents

- [Why it exists](#why-it-exists)
- [The journey, step by step](#the-journey-step-by-step)
- [Principles the code enforces](#principles-the-code-enforces)
- [Architecture](#architecture)
- [AI system design](#ai-system-design)
- [The analysis agents](#the-analysis-agents)
- [Findings: where each one came from and what you decided](#findings-where-each-one-came-from-and-what-you-decided)
- [The submission package](#the-submission-package)
- [Withholding invented transcripts](#withholding-invented-transcripts)
- [Running it](#running-it)
- [Settings](#settings)
- [API](#api)
- [Privacy](#privacy)
- [Tests and evaluation](#tests-and-evaluation)
- [Project layout](#project-layout)
- [Contributing](#contributing)
- [Responsible use and security](#responsible-use-and-security)
- [Acknowledgements](#acknowledgements)
- [Status and roadmap](#status-and-roadmap)
- [Further documentation](#further-documentation)

---

## Why it exists

People who witness serious crimes often hold the most direct evidence of them: footage on a phone,
a voice note, a screenshot. Getting that to investigators in a form they can use is hard:

- **The details that make a file credible are invisible** to the person holding it: capture time,
  GPS, device, and whether a file was forwarded or edited.
- **OTPLink is a plain web form.** It asks for a date, a place, a factual summary and the files, with
  limits on each. Nothing helps a person organise what they have before filling it in.
- **AI help can go wrong in ways people can't see.** A model can invent a transcript of a noisy
  clip, guess a place with false confidence, or write in legal language the person never meant to use.

ICCLexAI does the technical reading, shows the person everything it found and how it knows, and
leaves every decision with the person.

---

## The journey, step by step

There are five steps. You can move between them at any time, and each step ends with a button to
the next one.

### 1 · Files

Add photos, video, audio and documents. Each file is fingerprinted with SHA-256 when it arrives and
stored exactly as sent. Analysis starts straight away in the background, and a badge for each step
shows whether it is waiting, running, done, or not analysed.

![Files step](docs/screenshots/files.png)

### 2 · Review

Each finding carries a label saying where it came from: **From the file** (read directly) or
**AI suggestion** (a guess that can be wrong). You confirm, edit or reject each one. Conflicts are
put to you as questions. For example: "GPS in the file is 286 km from the place you said this
happened. Check which is right." A map shows the confirmed locations, and you can pin the exact spot.

![Review step](docs/screenshots/review.png)

### 3 · Your account

You give the incident a short name, and say when and where it happened. OTPLink requires both, and
dates and places found in your files are offered as suggestions. You also say where each file came
from (you recorded it, or who sent it to you, with a link). Then you can tell what happened, either
to an interview assistant that asks one gentle question at a time, or by writing statements yourself.

### 4 · Prepare

Before anything is built, a checklist shows what is ready and what is missing. You agree to send
your files exactly as you uploaded them, hidden details included, because those details help show
a file is genuine. One button then builds the submission. You can save a copy for your own records.

![Prepare step](docs/screenshots/prepare.png)

### 5 · Send

This step gives you the filing tools for OTPLink:

- You can check your files on your own device against the fingerprints. This happens in your browser
  and nothing is uploaded.
- Two safety checks come before OTPLink opens: whether you are on a trusted network without a VPN
  (which OTPLink asks for), and whether you will give your name or file anonymously.
- Every form field is shown in OTPLink's order, with a copy button and its length limit.
- The attachments are listed in order.
- Once you have filed, you can record it, with OTPLink's reference.

![Send step](docs/screenshots/send.png)

---

## Principles the code enforces

These are rules in code, the database and the tests, not only guidance.

| Principle | How it is enforced |
|---|---|
| **The person decides** | Only `confirmed` or `edited` findings can be cited in the package. Unreviewed and rejected findings are counted and left out, and the summary PDF says how many. |
| **No invented results** | An agent that cannot do its work (no key, no consent, a file type it doesn't handle, a model outage) marks the step **not analysed**. There are no fallback scores and no placeholder text. |
| **No legal conclusions** | The narrative may only state what a confirmed finding supports, and cites a finding for every sentence. Sentences that make legal claims ("clear jurisdiction", "a crime was committed") are dropped and shown to the person, never kept silently. |
| **Evidence is never changed** | Each original's hash is written once: a database trigger refuses any change. A file is re-hashed before it goes into a package. |
| **Every action is recorded** | The custody log is append-only and hash-chained: each event includes the hash of the one before. The database refuses UPDATE and DELETE on it. |
| **Findings are immutable** | A finding's content cannot change, only its status. An edit creates a new finding and marks the old one `superseded`, so a narrative sentence citing it is still traceable. |
| **AI use is disclosed** | Every package includes `ai_provenance.json` (which model produced which finding, through which job) and a plain-language statement of how AI was used. |
| **Outside services need consent** | Content goes to the AI provider or OpenStreetMap only if the person allowed it for that case. Without consent, only the local checks run. |

---

## Architecture

```mermaid
flowchart LR
    subgraph BR["Browser"]
        UI["React app<br/>5-step journey"]
    end
    subgraph SV["Server"]
        API["FastAPI<br/>icclex.main"]
        W["Worker<br/>icclex.worker"]
        FS[("Original files<br/>var/cases")]
        DB[("PostgreSQL 16 and PostGIS<br/>findings, jobs, custody log")]
    end
    subgraph EXT["Outside services (only with consent)"]
        G["Groq<br/>text, vision, speech"]
        OSM["OpenStreetMap<br/>Nominatim"]
    end
    OTP["ICC OTPLink"]

    UI -- "case key" --> API
    API --> DB
    API --> FS
    W -- "claims jobs<br/>FOR UPDATE SKIP LOCKED" --> DB
    W --> FS
    W --> G
    W --> OSM
    UI -. "the person files it themselves" .-> OTP
```

- **The API** receives uploads, serves findings, records each decision, and builds the package.
- **The worker** is a separate process. It claims analysis jobs from a database table, so there is
  no Redis or Celery to run. A network failure or rate limit is retried after a delay (60 s, then
  300 s); a crash is retried immediately. Failed or finished steps can be re-run from the API.
- **The database** carries the integrity rules: triggers, check constraints, the hash chain, and
  PostGIS geometry for locations.
- **Schema migrations** (Alembic): `0001` schema, `0002` integrity triggers, `0003` delayed retries
  and re-runs, `0004` dates read from file names.

The full design, with an entity-relationship diagram generated from the models, is in
[docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).

---

## AI system design

AI proposes and the person decides. There are eight AI components: six agents that read files, an
interview assistant, and a narrative writer. None of them can put anything in the submission. Their
output becomes a **proposed** finding or a draft, and only what the person confirms is used.

```mermaid
flowchart TD
    U["Upload<br/>SHA-256 fingerprint, custody event"] --> P["Plan for the file type<br/>(agents/__init__.py PLANS)"]
    P --> Q["Job queue<br/>one job per agent"]
    Q --> A1["metadata"] & A3["visual"] & A4["audio_video"] & A5["document"]
    A1 --> A2["geolocation"] & A6["integrity"]
    A4 --> G{"Transcript gate<br/>language, confidence,<br/>words per second"}
    A1 & A2 & A3 & A5 & A6 --> F["Proposed findings<br/>source: extracted or inferred"]
    G -- "passes" --> F
    G -- "fails" --> N["Not kept:<br/>listen to the file yourself"]
    I["Interview assistant"] --> S["Proposed stated facts"]
    F & S --> H{"The person reviews<br/>confirm, edit or reject"}
    H -- "confirmed or edited" --> C["Citable findings"]
    H -- "rejected" --> X["Left out, counted"]
    C --> W["Narrative writer<br/>every sentence cites findings"]
    W --> L{"Legal-claim filter"}
    L -- "kept" --> PK["Package<br/>summary.pdf, manifest,<br/>ai_provenance.json"]
    L -- "dropped" --> R["Shown to the person"]
```

### Components

| Component | Model | Reads | Produces | Rules it works within | When it can't work |
|---|---|---|---|---|---|
| `metadata` | none | EXIF and container metadata, the file name | capture time, GPS, device, file properties, file-name date (all `extracted`) | Reads only, nothing leaves the server. A file-name date is labelled as when an app saved the file. | Step says "not analysed" |
| `geolocation` | vision model, OpenStreetMap | metadata's GPS, keyframes, the stated place | place at the GPS point, ranked place candidates with reasons, distance conflict | Candidates are `inferred` and carry no coordinates. A conflict is put to the person as a question. | Without consent, only the distance check runs |
| `visual` | `qwen/qwen3.8-27b` | the image, or up to 3 keyframes per call | neutral description, text visible in the scene | People are described, never identified. App interface text is skipped. At most 1000 output tokens. | "not analysed", retried after a delay on network errors |
| `audio_video` | `whisper-large-v3-turbo` | audio extracted with ffmpeg | transcript | Kept only if it passes the [transcript gate](#withholding-invented-transcripts). Each attempt's score is recorded. | "no clear speech in an expected language; listen to the file yourself" |
| `document` | `openai/gpt-oss-120b` | document text, cut at a fixed length | names, dates, places, summary | The finding says when the text was cut, so a long document is never presented as fully read. | "not analysed" |
| `integrity` | none | bytes, metadata findings | consistency flags | A flag means "look at this", never "fake". It doesn't detect edited or AI-generated pixels. | Runs locally, always |
| Interview assistant | `openai/gpt-oss-120b` | what the person writes | the next question, and proposed `stated_fact` findings in the person's own words | One question at a time. The person can skip anything. It never presses for names, asks for the person's identity, gives legal advice or promises outcomes. It replies in the person's language. Conflicts with file dates are found by date arithmetic, not by the model. | Off without consent: the person writes statements themselves |
| Narrative writer | `openai/gpt-oss-120b` | confirmed and edited findings only, without file properties, device and integrity flags | the factual account in `summary.pdf` | Each sentence must cite findings, or it is dropped. A regular expression removes legal conclusions ("prima facie", "constitutes a war crime", "should be prosecuted"), and every removal is shown to the person. File dates are not presented as proof of when events happened. | A plain list of confirmed findings, each marked with its source |

### Run order for each file type

The planner reads the type from the file's bytes, then queues these jobs. An agent named after the
arrow waits for that agent to finish; the others start straight away.

| File type | Agents |
|---|---|
| Image | `metadata`, `geolocation` ← metadata, `visual`, `integrity` ← metadata |
| Video | `metadata`, `geolocation` ← metadata, `visual`, `audio_video`, `integrity` ← metadata |
| Audio | `metadata`, `audio_video`, `integrity` ← metadata |
| Document | `metadata`, `document`, `integrity` ← metadata |
| Anything else | `metadata`, `integrity` ← metadata |

### Where people stay in charge

- **Every finding starts as proposed.** Confirming, editing or rejecting it is the only way it reaches
  the package, and edits keep the original as `superseded`.
- **Re-analysis never deletes.** Re-running a step supersedes its earlier findings and leaves alone
  any finding the person edited.
- **The person gives the date and place.** Files only suggest them.
- **The person agrees to send their files** at the Prepare step, and **clicks Submit** on OTPLink.
- **Every AI contribution is traceable.** `ai_provenance.json` lists each finding, the job and model
  that produced it, and whether it was read from the file, inferred, or stated by the person.

## The analysis agents

An agent is a function from one file to a list of findings. It never touches the database: the
worker validates what it returns and stores it, in one transaction, together with the job, the model,
the agent version and a custody event.

| Agent | Shown as | What it reports | Leaves the server? |
|---|---|---|---|
| `metadata` | File details | Capture time, GPS, device and file properties from EXIF and container metadata. Dates in file names such as `WhatsApp Video 2025-06-17 at 22.46.40`, labelled as when an app saved the file. | No |
| `geolocation` | Location | The place at the file's GPS point (reverse geocoded). Place candidates from visible clues, ranked, each with its reasons. A flag when the file's GPS and the stated place are far apart. | With consent: OpenStreetMap, vision model |
| `visual` | What it shows | A neutral description of what is visible, and any text in the scene (signs, captions, usernames), copied out. People are described, never identified. App interface text is skipped. | With consent: vision model |
| `audio_video` | Speech | A transcript, kept only if it passes the confidence checks ([see below](#withholding-invented-transcripts)). Otherwise the step says to listen to the file yourself. | With consent: speech model |
| `document` | Document text | Names, dates, places and a summary from a document's text. A long document is cut, and the finding says so. | With consent: text model |
| `integrity` | Checks | Consistency flags, for example a file extension that doesn't match its content, or metadata contradicting itself. A flag means "look at this", never "fake". | No |

File type is detected from the bytes, not from the name or what the browser reports
(`icclex/sniff.py`). The integrity agent reports when they disagree.

**Models (Groq), checked on 2026-11-06:** `openai/gpt-oss-120b` for text, `qwen/qwen3.8-27b` for
vision (at most 3 images and 1000 output tokens per call on the free tier, so frames are sent in
batches), and `whisper-large-v3-turbo` for speech.

---

## Findings: where each one came from and what you decided

Every finding has a **kind**, a **source** and a **status**.

- **Kinds:** `capture_time`, `name_date`, `gps`, `place`, `place_candidate`, `device`,
  `file_properties`, `description`, `visible_text`, `transcript`, `entity`, `document_summary`,
  `integrity_flag`, `geo_conflict`, `stated_fact`
- **Sources:**
  - `extracted`: read directly from the file
  - `inferred`: an AI suggestion
  - `stated`: what the person said
- **Statuses:** `proposed`, then `confirmed`, `edited` or `rejected`. `superseded` marks a finding
  replaced by an edit or a re-analysis.

A file's date is when it was made or saved, which may not be when the event happened. The interface
and the summary say so wherever a file date is offered.

---

## The submission package

The package is the person's record of what goes to OTPLink. **It holds no copies of the files.** The
person attaches their own originals, and the manifest proves each attachment is the file that was
analysed.

| File | Contents |
|---|---|
| `README_FIRST.txt` | What the package is, and that it holds no copy of your files |
| `summary.pdf` | The factual account, built from confirmed findings with a citation for every sentence, plus a timeline and a section for each file |
| `manifest.json` / `manifest.csv` | For each file: label, original name, type, size, SHA-256, and the confirmed findings |
| `evidence_map.geojson` | Confirmed locations |
| `custody_log.csv` | The full hash-chained custody log |
| `otplink_fields.md` / `.json` | The text for each OTPLink field, in form order, with limit warnings |
| `ai_provenance.json` | Which model produced which finding, and the statement of how AI was used |

Building a package needs: analysis finished, at least one confirmed finding, a date and a place, and
the person's consent to send their files exactly as uploaded. Changing a finding afterwards marks the
package **stale**, and it must be prepared again.

OTPLink's fields and limits, as checked on the live form, are in
[docs/otplink-field-map.md](docs/otplink-field-map.md).

---

## Withholding invented transcripts

On 2026-11-06, Whisper turned two Nairobi street clips into Spanish ("¡Adiós!") and Malay
("Terima kasih"). Speech models invent fluent text from noise, and these transcripts would have
reached review looking just like real ones.

A transcript is now kept only if all of these hold:

1. **The language is expected:** one of `ICCLEX_SPEECH_LANGUAGES` (default English and Swahili). If
   the auto-detected pass fails, the clip is transcribed again with each expected language forced.
2. **The model is confident:** the average log-probability, weighted by duration, is at least −0.6
   (−0.5 on a forced-language pass).
3. **The speech is dense enough:** at least 0.5 words per second.

When no pass qualifies, the step says *"no clear speech in an expected language; listen to the file
yourself"*, followed by the score of each attempt.

These limits were measured on 180 clips from FLEURS (Swahili and English, clean and with added noise,
plus clips with no speech at all). **Invented transcripts of no-speech clips fell from 57% to 3%,
while 73% of speech clips still got an accurate transcript.** Noisy Swahili remains weak, which is a
limit of the model, and there is no Sheng in the evaluation set. See
[evals/transcription/README.md](evals/transcription/README.md).

---

## Running it

**You need:** Python 3.10+, Node 18+, Docker (for the database), and `ffmpeg`/`ffprobe` on `PATH`.

```bash
cp .env.example .env                          # add GROQ_API_KEY and the model names
docker compose up -d db                       # PostgreSQL 16 + PostGIS on 127.0.0.1:5433

cd apps/backend
pip install -r requirements.txt
alembic upgrade head
uvicorn icclex.main:app --port 8002           # API (terminal 1)
python -m icclex.worker                       # analysis worker (terminal 2)

cd ../frontend
npm install && npm run dev                    # http://localhost:5173 (terminal 3)
```

**Shortcuts:**
- `python launch_icc_system_clean.py` starts the API, worker and frontend together.
- `docker compose up --build` starts the database, migrations, API and worker in containers.

Check that it's up: `curl localhost:8002/api/health` reports the database's schema revision, which should
be `0004`.

---

## Settings

Environment variables, read from `.env` if present (`apps/backend/icclex/config.py`).

| Variable | Purpose |
|---|---|
| `ICCLEX_DATABASE_URL` | Default `postgresql+psycopg://icclex:icclex@localhost:5433/icclex` |
| `ICCLEX_STORAGE_ROOT` | Where originals and derived files live (default `var/cases`, git-ignored) |
| `GROQ_API_KEY` | Needed by every step that calls a model |
| `ICCLEX_TEXT_MODEL` | Interviewer, narrative, documents. **No default.** Verified: `openai/gpt-oss-120b` |
| `ICCLEX_VISION_MODEL` | Descriptions, scene text, place clues. **No default.** Verified: `qwen/qwen3.8-27b` |
| `ICCLEX_VISION_MAX_IMAGES` / `ICCLEX_VISION_MAX_TOKENS` | Per-call caps (default 3 and 1000, that model's free-tier limits on Groq) |
| `ICCLEX_TRANSCRIBE_MODEL` | Speech to text (default `whisper-large-v3-turbo`) |
| `ICCLEX_SPEECH_LANGUAGES` | Languages a transcript may be in, as `code:name` pairs (default `en:english,sw:swahili`) |
| `ICCLEX_CORS_ORIGINS` | Allowed browser origins (default `http://localhost:5173`) |
| `ICCLEX_NOMINATIM_USER_AGENT` | Identifies you to OpenStreetMap's geocoder, as its usage policy requires |
| `VITE_API_URL` | The frontend's API address (default `http://localhost:8002`) |

A model that isn't set makes its step show "not analysed". The text model has no default because the
one the old code used (`llama-3.3-70b-versatile`) returned "does not exist or you do not have access"
on 2026-11-06. Name a model your account can use.

---

## API

Every case route needs the case's bearer token, from the case key.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/cases` | Create a case. Returns the case id and a token, shown once. |
| `GET` / `PATCH` | `/cases/{id}` | Read the case, or set its name, dates, place and consent |
| `POST` | `/cases/{id}/evidence` | Upload files; analysis jobs are queued |
| `GET` | `/cases/{id}/evidence/{eid}/content` | The original file |
| `POST` | `/cases/{id}/evidence/{eid}/rerun` | Re-run failed steps, or named finished ones (their earlier findings are superseded) |
| `GET` | `/cases/{id}/findings` | All current findings |
| `PATCH` | `/cases/{id}/findings/{fid}` | Confirm, reject or edit a finding |
| `POST` | `/cases/{id}/findings/bulk` | Confirm or reject several at once |
| `POST` | `/cases/{id}/facts` | Add a statement, optionally tied to a file (where it came from) |
| `POST` | `/cases/{id}/interview` | One turn with the interview assistant |
| `GET` | `/cases/{id}/custody` | The custody log, with the chain verified |
| `POST` | `/cases/{id}/package` | Build the package (needs consent, a date and a place) |
| `GET` | `/cases/{id}/package/download` | The package zip |
| `GET` | `/cases/{id}/package/otplink` | The OTPLink field text for the current package |
| `POST` | `/cases/{id}/filed` | Record that the person filed it, with an optional reference |

---

## Privacy

- **No account.** A case is opened with a case key. The server stores only the key's hash, so a lost
  key cannot be recovered, and nobody, including the operators, can open a case without it.
- **Consent for each case.** Images, audio, document text and chat go to the AI provider, and GPS
  points go to OpenStreetMap, only if the person ticks the box. Without it, the local checks still run:
  file details, consistency checks, and distance to the stated place.
- **No IP addresses or user agents are stored.**
- **A blank map by default.** Points are drawn on a blank background. Street tiles, which would tell
  openstreetmap.org which area you're looking at, load only if you ask for them.
- **Files go as they are.** Nothing is removed from the originals. The person agrees, at the Prepare
  step, to send them with their hidden details, because those details help show a file is genuine.

---

## Tests and evaluation

```bash
docker compose up -d db
python -m pytest tests          # needs PostgreSQL; FAILS rather than skips if it isn't reachable
```

The tests run against a real PostgreSQL + PostGIS database built from the migrations, because the
triggers, constraints and `SKIP LOCKED` queue exist nowhere else. They blank the model settings, so
they can't reach an outside service. 97 tests cover the API and authentication, agents, database
integrity, intake, the narrative, packages, re-hash verification, and that the ER diagram in the
design doc matches the models.

The transcription gate has its own evaluation, which downloads about 10 MB per language:

```bash
python evals/transcription/build.py --per-language 25
python evals/transcription/run.py               # calls Whisper only for what isn't cached
python evals/transcription/run.py --offline     # re-report from the cache
```

---

## Project layout

```text
ICCLexAI/
├── apps/
│   ├── backend/
│   │   ├── icclex/                  FastAPI app
│   │   │   ├── agents/              analysis agents and the Groq wrapper
│   │   │   │   ├── metadata.py      capture time, GPS, device, file-name dates
│   │   │   │   ├── geolocation.py   GPS place, visible-clue candidates, conflicts
│   │   │   │   ├── visual.py        what is visible, scene text
│   │   │   │   ├── audio_video.py   transcripts behind the confidence gate
│   │   │   │   ├── document.py      entities, dates, places, summary
│   │   │   │   ├── integrity.py     consistency flags
│   │   │   │   ├── frames.py        video keyframes
│   │   │   │   ├── base.py          the agent contract
│   │   │   │   └── llm.py           Groq calls and error mapping
│   │   │   ├── main.py              app, CORS, /api/health
│   │   │   ├── routes.py            every case endpoint
│   │   │   ├── models.py            SQLAlchemy models
│   │   │   ├── schemas.py           request and response shapes
│   │   │   ├── jobs.py              SKIP LOCKED job queue, re-runs
│   │   │   ├── worker.py            runs one agent per job
│   │   │   ├── custody.py           hash-chained custody log
│   │   │   ├── interview.py         the interview assistant
│   │   │   ├── narrative.py         cited account, legal-claim filter
│   │   │   ├── package.py           package, OTPLink fields, AI provenance
│   │   │   └── timeline.py · verify.py · sniff.py · storage.py · config.py · erd.py
│   │   └── migrations/versions/     0001 schema … 0004 file-name dates
│   └── frontend/
│       └── src/
│           ├── components/case/     CaseApp, one panel per step, FilingAssistant, MapPanel
│           ├── components/ui/       Button, Card
│           ├── lib/                 api.ts, findings.ts, session.ts
│           └── index.css            navy, teal and gold theme
├── docs/                            design, OTPLink field map, checklist, screenshots/
├── evals/transcription/             FLEURS build and run for the transcript gate
├── tests/                           pytest suite against real PostgreSQL
├── docker/ · docker-compose.yml     API image, database, worker
├── libs/icc_automation/             older agents, unused by the backend
└── ARCHIVED_REDUNDANT/              previous implementations, kept for reference
```

| Path | What lives there |
|---|---|
| `apps/backend/icclex/` | API (`routes.py`), models, job queue and worker, custody log, interview, narrative, package builder |
| `apps/backend/icclex/agents/` | The analysis agents and the Groq wrapper (`llm.py`) |
| `apps/backend/migrations/` | Alembic migrations `0001`–`0004` |
| `apps/frontend/src/components/case/` | The React UI: one panel for each step, the filing assistant, the map |
| `apps/frontend/src/components/ui/` | Shared buttons and cards (navy, teal and gold theme in `src/index.css`) |
| `evals/transcription/` | The transcript-gate evaluation on FLEURS |
| `docs/` | System design, OTPLink field map, checklist, case workflow, screenshots |
| `tests/` | The test suite |
| `libs/icc_automation/` | Older agents the backend no longer uses, kept until the new agents are accepted |
| `ARCHIVED_REDUNDANT/` | Previous backends, launchers, chat and validation UIs, kept for reference |

---

## Status and roadmap

**Working now:** the five-step journey, all six agents with real models, delayed retries and
re-analysis, the transcript gate, packages without copies of the files, AI provenance, and the
filing assistant.

**Next:**
- **Assisted sending.** A browser on the server fills in the OTPLink form, and the person watches it
  live, ticks the reCAPTCHA and clicks Submit themselves. The OTPLink reference is then read from the
  confirmation page. The tool will never solve the captcha or submit for the person.
- **Pre-filling when and where.** Use the person's own account first, then file-name dates and the
  best place suggestion, for the person to confirm with one click.
- Show the model name on each AI suggestion, and record a hash of each prompt in the provenance file.
- Label real Swahili and Sheng field recordings for the transcription evaluation.

The full list of what is done, checked and still open is in [docs/CHECKLIST.md](docs/CHECKLIST.md).

---

## Contributing

Issues and pull requests are welcome. Before opening one:

1. Run the tests against a real database: `docker compose up -d db && python -m pytest tests`.
2. If you change the schema, add an Alembic migration and regenerate the ER diagram with
   `python -m icclex.erd`. A test checks that the diagram matches the models.
3. If you change the transcription model or its limits, rerun `evals/transcription/run.py` and put the
   new numbers in the pull request.
4. Keep the core rules: no fallback scores, no legal conclusions, and nothing in the package that the
   person didn't confirm.

Comments here record the incident that made a rule necessary (what went wrong, and when), not only
what the code does. Please follow that.

## Responsible use and security

- This tool handles material about serious crimes, from people who may be at risk. Deploy it only
  where you can protect the server, the stored files and the database.
- Never test against OTPLink by submitting. The ICC's portal is for real submissions.
- Report vulnerabilities privately through GitHub's security advisories, not in a public issue.

## Acknowledgements

- [FLEURS](https://huggingface.co/datasets/google/fleurs) (Google), the speech used to measure the transcript gate
- [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors and Nominatim, for place names
- [Groq](https://groq.com), for model hosting
- [Leaflet](https://leafletjs.com), [Lucide](https://lucide.dev), FastAPI, SQLAlchemy and PostGIS

## Further documentation

- [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md): design, schema and ER diagram
- [docs/otplink-field-map.md](docs/otplink-field-map.md): OTPLink's live form fields and limits
- [docs/CHECKLIST.md](docs/CHECKLIST.md): done, verified and open
- [evals/transcription/README.md](evals/transcription/README.md): the transcription evaluation

## Licence

See [LICENSE](LICENSE).
