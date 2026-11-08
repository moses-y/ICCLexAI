"""Schema from the plan's data model. Fact rows are never overwritten: an edited finding is a new
row whose supersedes_id points at the one it replaces."""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    REAL,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSTZRANGE, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

CASE_STATUSES = ("draft", "analysing", "review", "package_ready", "filed_by_user")
EVIDENCE_STATUSES = ("received", "analysing", "analysed", "failed")
JOB_STATUSES = ("queued", "running", "done", "failed")
AGENTS = ("metadata", "geolocation", "visual", "audio_video", "document", "integrity")
FINDING_KINDS = (
    "capture_time", "gps", "device", "file_properties", "place", "place_candidate", "description", "visible_text", "transcript",
    "entity", "document_summary", "integrity_flag", "geo_conflict", "stated_fact", "name_date",
)
FINDING_SOURCES = ("extracted", "inferred", "stated")
# 'superseded' is not in the plan's list: an edited finding needs its predecessor marked so that a
# narrative claim citing it can be told apart from one citing the current value.
FINDING_STATUSES = ("proposed", "confirmed", "edited", "rejected", "superseded")
CITABLE_STATUSES = ("confirmed", "edited")
ARTEFACT_KINDS = ("keyframe", "thumbnail", "transcript_file", "stripped_copy", "summary_pdf", "manifest", "package_zip")
CUSTODY_EVENT_TYPES = (
    "case_created", "received", "hash_verified", "hash_mismatch", "analysed", "analysis_failed",
    "finding_changed", "exported", "package_built", "filed", "reanalysis_requested",
)
GENESIS_HASH = "0" * 64


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _created() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Submitter(Base):
    __tablename__ = "submitter"
    id: Mapped[uuid.UUID] = _pk()
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(Text)
    contact_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = _created()


class Case(Base):
    __tablename__ = "case"
    id: Mapped[uuid.UUID] = _pk()
    submitter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("submitter.id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    incident_name: Mapped[str | None] = mapped_column(Text)
    incident_period = mapped_column(TSTZRANGE)
    incident_location = mapped_column(Geography("POINT", srid=4326, spatial_index=False))
    incident_location_text: Mapped[str | None] = mapped_column(Text)
    narrative_language: Mapped[str] = mapped_column(Text, nullable=False, default="en")
    # Images, audio and text leave this server for third-party model and geocoding services only
    # when the submitter has agreed. Not in the plan's schema: added when the agents were written.
    external_processing_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    otp_reference: Mapped[str | None] = mapped_column(Text)
    filed_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _created()
    __table_args__ = (CheckConstraint(_in("status", CASE_STATUSES), name="ck_case_status"),)


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(Text, nullable=False)
    mime_sniffed: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(Text, nullable=False)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="received")
    received_at: Mapped[datetime] = _created()
    created_at: Mapped[datetime] = _created()
    __table_args__ = (
        CheckConstraint(_in("status", EVIDENCE_STATUSES), name="ck_evidence_status"),
        UniqueConstraint("case_id", "sha256", name="uq_evidence_case_sha256"),
    )


class AnalysisJob(Base):
    __tablename__ = "analysis_job"
    id: Mapped[uuid.UUID] = _pk()
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), nullable=False, index=True)
    agent: Mapped[str] = mapped_column(Text, nullable=False)
    # Geolocation reads the metadata agent's GPS findings, so it waits for that job to finish.
    depends_on_agent: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    # A job retried after a network error or rate limit is not claimed again before this time.
    not_before: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _created()
    __table_args__ = (
        CheckConstraint(_in("status", JOB_STATUSES), name="ck_job_status"),
        CheckConstraint(_in("agent", AGENTS), name="ck_job_agent"),
        UniqueConstraint("evidence_id", "agent", name="uq_job_evidence_agent"),
        Index("ix_job_queue", "status", "created_at"),
    )


class Finding(Base):
    __tablename__ = "finding"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("analysis_job.id"))
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    value = mapped_column(JSONB, nullable=False)
    geom = mapped_column(Geography("POINT", srid=4326, spatial_index=False))
    source: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(REAL)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="proposed")
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("finding.id"))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _created()
    __table_args__ = (
        CheckConstraint(_in("kind", FINDING_KINDS), name="ck_finding_kind"),
        CheckConstraint(_in("source", FINDING_SOURCES), name="ck_finding_source"),
        CheckConstraint(_in("status", FINDING_STATUSES), name="ck_finding_status"),
        CheckConstraint("confidence IS NULL OR source = 'inferred'", name="ck_finding_confidence_inferred_only"),
        Index("ix_finding_case_kind", "case_id", "kind"),
        Index("ix_finding_evidence", "evidence_id"),
    )


class Artefact(Base):
    __tablename__ = "artefact"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("analysis_job.id"))
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (CheckConstraint(_in("kind", ARTEFACT_KINDS), name="ck_artefact_kind"),)


class CustodyEvent(Base):
    __tablename__ = "custody_event"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("evidence.id"))
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_ref: Mapped[str] = mapped_column(Text, nullable=False)
    detail = mapped_column(JSONB, nullable=False)
    prev_event_hash: Mapped[str] = mapped_column(Text, nullable=False)
    event_hash: Mapped[str] = mapped_column(Text, nullable=False)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (
        CheckConstraint(_in("event_type", CUSTODY_EVENT_TYPES), name="ck_custody_event_type"),
        CheckConstraint(_in("actor_type", ("user", "agent", "system")), name="ck_custody_actor_type"),
        UniqueConstraint("case_id", "prev_event_hash", name="uq_custody_chain_no_fork"),
    )


class TimelineEvent(Base):
    __tablename__ = "timeline_event"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    time_precision: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _created()
    findings = relationship("TimelineEventFinding", cascade="all, delete-orphan")
    __table_args__ = (
        CheckConstraint(_in("time_precision", ("exact", "day", "month", "unknown")), name="ck_timeline_precision"),
    )


class TimelineEventFinding(Base):
    __tablename__ = "timeline_event_finding"
    timeline_event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("timeline_event.id"), primary_key=True)
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("finding.id"), primary_key=True)


class Narrative(Base):
    __tablename__ = "narrative"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    created_at: Mapped[datetime] = _created()
    claims = relationship("NarrativeClaim", cascade="all, delete-orphan", order_by="NarrativeClaim.sentence_index")
    __table_args__ = (
        CheckConstraint(_in("status", ("draft", "approved", "stale")), name="ck_narrative_status"),
        UniqueConstraint("case_id", "version", name="uq_narrative_case_version"),
    )


class NarrativeClaim(Base):
    __tablename__ = "narrative_claim"
    id: Mapped[uuid.UUID] = _pk()
    narrative_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("narrative.id"), nullable=False, index=True)
    sentence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # No citation, no claim. The finding must be confirmed or edited (trigger, migration 0002).
    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("finding.id"), nullable=False)


class SubmissionPackage(Base):
    __tablename__ = "submission_package"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    narrative_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("narrative.id"), nullable=False)
    zip_artefact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("artefact.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="current")
    created_at: Mapped[datetime] = _created()
    __table_args__ = (
        CheckConstraint(_in("status", ("current", "stale")), name="ck_package_status"),
        UniqueConstraint("case_id", "version", name="uq_package_case_version"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_message"
    id: Mapped[uuid.UUID] = _pk()
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (CheckConstraint(_in("role", ("user", "assistant")), name="ck_chat_role"),)
