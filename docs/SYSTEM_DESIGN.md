# ICCLexAI system design

What the system is: it helps a person turn their own evidence (photos, video, audio, documents) and
their account into a **package they file themselves on the ICC Prosecutor's OTPLink portal**. Agents
read each file, say what they found and how they know, and the person confirms, edits or rejects every
finding. Nothing is submitted for them: OTPLink has no public API and no published terms allowing
automation, so the system ends at a package and a checklist.

On 2026-11-05 the previous version ran every analysis step as a mock, replaced uploaded binaries with
the text `[Binary file: x]`, deleted the only copy of each file, and told users a case had been
submitted to the ICC when nothing was sent. The design below exists so none of that can recur.

## Rules the design enforces

| Rule | Where it is enforced |
|---|---|
| An original is never altered or lost | stored read-only, hashed while streaming; `evidence` hash/size/path are write-once (trigger); nightly re-hash (`verify.py`) |
| Every fact says where it came from | `finding.source` is `extracted` (read from the file), `inferred` (a model said so) or `stated` (the submitter); confidence exists only for `inferred` (check constraint) |
| The submitter confirms before anything is used | only `confirmed` or `edited` findings reach the narrative and package; a narrative claim citing anything else is rejected by the database |
| No legal conclusions | `narrative.py` drops sentences that state one and reports them; the agents are told not to |
| A model outage never produces invented output | agents raise `AgentUnavailable`; the job fails and the file shows "not analysed" |
| Content leaves the server only with consent | `case.external_processing_consent`; agents that call a model or geocoder refuse without it |
| The chain of custody cannot be quietly edited | `custody_event` is append-only and hash-chained (trigger + `custody.verify_chain`) |
| The tool never says it filed anything | the case reaches `filed_by_user` only when the submitter says so, and the log records that it is unverified |

## Components

```mermaid
flowchart LR
    subgraph Client
        UI["React UI<br/>(Vite, Leaflet)"]
    end
    subgraph Backend["Backend (apps/backend/icclex)"]
        API["FastAPI<br/>cases, upload, findings,<br/>interview, package"]
        W["Worker process<br/>claims analysis_job rows"]
        subgraph Agents["Agents: one file in, findings out"]
            A1["metadata"]
            A2["geolocation"]
            A3["visual"]
            A4["audio_video"]
            A5["document"]
            A6["integrity"]
        end
        subgraph Case["Case building"]
            C1["interviewer"]
            C2["timeline"]
            C3["narrative<br/>(citation-checked)"]
            C4["package builder"]
        end
    end
    DB[("PostgreSQL 16 + PostGIS<br/>cases, findings, custody log,<br/>job queue")]
    OBJ[("File store<br/>originals read-only,<br/>derived files")]
    subgraph Ext["External services (only with consent)"]
        LLM["Groq: text, vision, Whisper"]
        GEO["Nominatim<br/>(cached, 1 request/s)"]
    end
    UI <--> API
    API --> DB
    API --> OBJ
    W -->|"FOR UPDATE SKIP LOCKED"| DB
    W --> Agents
    W --> OBJ
    A2 --> GEO
    A3 --> LLM
    A4 --> LLM
    A5 --> LLM
    API --> Case
    C1 --> LLM
    C3 --> LLM
    Case --> DB
```

Local-only agents (no consent needed): `metadata`, `integrity`, and the distance check inside
`geolocation`. The job queue is a table, so there is no Redis to run. Agents never write to the
database; the worker validates what they return and stores it with the job, model and version in one
transaction.

## Request flow

```mermaid
sequenceDiagram
    actor U as Submitter
    participant UI as React UI
    participant API as FastAPI
    participant OBJ as File store
    participant DB as PostgreSQL
    participant W as Worker
    participant AG as Agents
    U->>UI: add a file
    UI->>API: POST /cases/{id}/evidence (stream)
    API->>OBJ: write original, SHA-256 while streaming, read-only
    API->>DB: evidence + custody_event(received) + analysis_jobs
    API-->>UI: evidence id and sha256
    W->>DB: claim a job (SKIP LOCKED; waits for its dependency)
    W->>OBJ: read the original
    W->>AG: run the agent
    AG-->>W: findings (extracted / inferred) or AgentUnavailable
    W->>DB: findings, job result, custody_event(analysed)
    UI->>API: poll
    U->>UI: confirm / edit / reject findings
    UI->>API: PATCH /findings/{id}
    API->>DB: finding status (an edit is a new row), custody_event
    U->>UI: describe the incident
    API->>DB: stated findings; date conflicts put to the submitter
    U->>UI: build package
    API->>DB: timeline, narrative + claims, package, custody_event
    API-->>UI: package ready
    U->>UI: download and file on OTPLink
    U->>UI: "I filed it" (optional reference)
    API->>DB: status filed_by_user (reported, not verified)
```

## Case lifecycle

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> analysing: file uploaded
    analysing --> review: every job finished or failed
    review --> analysing: more files added
    review --> package_ready: package built
    package_ready --> review: a finding changed (package becomes stale)
    package_ready --> filed_by_user: submitter says they filed
    filed_by_user --> [*]
```

## Data model

Generated from the tables by `python -m icclex.erd`; `tests/test_erd_doc.py` fails if this block and
the schema disagree. Fact rows are never overwritten: an edit adds a finding whose `supersedes_id`
points at the old one, and the old one becomes `superseded`.

<!-- erd:start -->
```mermaid
erDiagram
    EVIDENCE ||--o{ ANALYSIS_JOB : "evidence_id"
    CASE ||--o{ ARTEFACT : "case_id"
    EVIDENCE |o--o{ ARTEFACT : "evidence_id"
    ANALYSIS_JOB |o--o{ ARTEFACT : "job_id"
    SUBMITTER |o--o{ CASE : "submitter_id"
    CASE ||--o{ CHAT_MESSAGE : "case_id"
    CASE ||--o{ CUSTODY_EVENT : "case_id"
    EVIDENCE |o--o{ CUSTODY_EVENT : "evidence_id"
    CASE ||--o{ EVIDENCE : "case_id"
    CASE ||--o{ FINDING : "case_id"
    EVIDENCE |o--o{ FINDING : "evidence_id"
    ANALYSIS_JOB |o--o{ FINDING : "job_id"
    FINDING |o--o{ FINDING : "supersedes_id"
    CASE ||--o{ NARRATIVE : "case_id"
    NARRATIVE ||--o{ NARRATIVE_CLAIM : "narrative_id"
    FINDING ||--o{ NARRATIVE_CLAIM : "finding_id"
    CASE ||--o{ SUBMISSION_PACKAGE : "case_id"
    NARRATIVE ||--o{ SUBMISSION_PACKAGE : "narrative_id"
    ARTEFACT ||--o{ SUBMISSION_PACKAGE : "zip_artefact_id"
    CASE ||--o{ TIMELINE_EVENT : "case_id"
    TIMELINE_EVENT ||--o{ TIMELINE_EVENT_FINDING : "timeline_event_id"
    FINDING ||--o{ TIMELINE_EVENT_FINDING : "finding_id"
    ANALYSIS_JOB {
        UUID id PK
        UUID evidence_id FK
        TEXT agent
        TEXT depends_on_agent
        TEXT status
        INTEGER attempts
        TEXT model
        TEXT model_version
        TEXT error
        DATETIME not_before
        DATETIME started_at
        DATETIME finished_at
        DATETIME created_at
    }
    ARTEFACT {
        UUID id PK
        UUID case_id FK
        UUID evidence_id FK
        UUID job_id FK
        TEXT kind
        TEXT storage_uri
        TEXT sha256
        DATETIME created_at
    }
    CASE {
        UUID id PK
        UUID submitter_id FK
        TEXT status
        TEXT incident_name
        TSTZRANGE incident_period
        geography(POINT_4326) incident_location
        TEXT incident_location_text
        TEXT narrative_language
        BOOLEAN external_processing_consent
        TEXT otp_reference
        DATETIME filed_confirmed_at
        DATETIME created_at
    }
    CHAT_MESSAGE {
        UUID id PK
        UUID case_id FK
        TEXT role
        TEXT content
        DATETIME created_at
    }
    CUSTODY_EVENT {
        UUID id PK
        UUID case_id FK
        UUID evidence_id FK
        TEXT event_type
        TEXT actor_type
        TEXT actor_ref
        JSONB detail
        TEXT prev_event_hash
        TEXT event_hash
        DATETIME at
        DATETIME created_at
    }
    EVIDENCE {
        UUID id PK
        UUID case_id FK
        TEXT original_name
        TEXT mime_sniffed
        BIGINT size_bytes
        TEXT sha256
        TEXT storage_uri
        TEXT status
        DATETIME received_at
        DATETIME created_at
    }
    FINDING {
        UUID id PK
        UUID case_id FK
        UUID evidence_id FK
        UUID job_id FK
        TEXT kind
        JSONB value
        geography(POINT_4326) geom
        TEXT source
        REAL confidence
        TEXT status
        UUID supersedes_id FK
        DATETIME confirmed_at
        DATETIME created_at
    }
    NARRATIVE {
        UUID id PK
        UUID case_id FK
        INTEGER version
        TEXT body
        TEXT model
        TEXT status
        DATETIME created_at
    }
    NARRATIVE_CLAIM {
        UUID id PK
        UUID narrative_id FK
        INTEGER sentence_index
        TEXT text
        UUID finding_id FK
    }
    SUBMISSION_PACKAGE {
        UUID id PK
        UUID case_id FK
        UUID narrative_id FK
        UUID zip_artefact_id FK
        INTEGER version
        TEXT manifest_sha256
        TEXT status
        DATETIME created_at
    }
    SUBMITTER {
        UUID id PK
        TEXT token_hash
        TEXT display_name
        BLOB contact_encrypted
        DATETIME created_at
    }
    TIMELINE_EVENT {
        UUID id PK
        UUID case_id FK
        DATETIME occurred_at
        TEXT time_precision
        TEXT label
        DATETIME created_at
    }
    TIMELINE_EVENT_FINDING {
        UUID timeline_event_id PK,FK
        UUID finding_id PK,FK
    }
```
<!-- erd:end -->

Changes from the first design, made while building:
- `finding.status` gains `superseded`, and `finding.kind` gains `device` and `file_properties`.
- `analysis_job.depends_on_agent`: geolocation and integrity read the metadata agent's findings, so the queue holds them back until it finishes.
- `case.external_processing_consent`, `case.incident_location_text` and `case.narrative_language`.
- A `timeline_event.time_precision` of `exact`, `day`, `month` or `unknown`.

Database guarantees (migration `0002_integrity_triggers`): evidence hash, size, path and case are
write-once; `custody_event` refuses UPDATE, DELETE and TRUNCATE, and `(case_id, prev_event_hash)` is
unique so the chain cannot fork; a finding's content cannot be rewritten, only its review status;
a narrative claim must cite a confirmed or edited finding.

## Known limits

- **OTPLink fields are provisional.** `docs/otplink-field-map.md` records what is and is not verified. A person has to walk through the live form before the field text can be relied on.
- **No tamper or AI-image detector.** The integrity agent compares metadata and raises flags ("worth checking"); it cannot show a file is authentic or fake.
- **Metadata stripping** is lossless and covers JPEG and PNG only. Other types go in unchanged and the package says so.
- **The last custody event can be deleted only by disabling the trigger**, and the chain would still verify, because the log stores no external anchor for its tip. Anchoring the tip outside the database (for example in the package manifest of a case already handed over) is not built.
- **Translation and OCR beyond what the vision model copies** are not built; OTPLink is English only.
- **One server, local disk.** The storage interface (`storage.py`) is the seam for S3-compatible storage.
