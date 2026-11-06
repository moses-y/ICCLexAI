"""The agent contract. An agent is a function from one evidence item to findings. It never touches
the database: the worker validates what it returns and stores it with the job, model and version.

If an agent cannot do its work (no key, no consent, unsupported file) it raises AgentUnavailable.
The job is marked failed and the evidence shows "not analysed". There are no fallback scores."""

from dataclasses import dataclass, field
from pathlib import Path


class AgentUnavailable(Exception):
    """The agent could not run. The message is shown to the submitter."""


@dataclass
class FindingDraft:
    kind: str
    value: dict
    source: str  # "extracted" (read from the file) or "inferred" (a model said so)
    confidence: float | None = None  # inferred findings only
    geom: tuple[float, float] | None = None  # (lat, lon)


@dataclass
class ArtefactDraft:
    kind: str
    filename: str
    data: bytes


@dataclass
class AgentContext:
    evidence_id: str
    case_id: str
    path: Path
    mime: str
    original_name: str
    external_consent: bool
    prior_findings: list[dict] = field(default_factory=list)  # findings already stored for this evidence
    case_location: tuple[float, float] | None = None  # (lat, lon) the submitter says it happened


@dataclass
class AgentResult:
    findings: list[FindingDraft] = field(default_factory=list)
    artefacts: list[ArtefactDraft] = field(default_factory=list)
    model: str | None = None
    model_version: str | None = None
    notes: list[str] = field(default_factory=list)  # parts skipped; stored on the job, shown to the submitter


NEEDS_EXTERNAL = (
    "This step sends the file's content to a third-party service. It was not run because the "
    "submitter has not agreed to external processing for this case."
)


def require_consent(ctx: AgentContext) -> None:
    if not ctx.external_consent:
        raise AgentUnavailable(NEEDS_EXTERNAL)
