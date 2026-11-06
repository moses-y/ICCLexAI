from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    incident_name: str | None = None
    external_processing_consent: bool = False


class CaseUpdate(BaseModel):
    incident_name: str | None = None
    incident_location_text: str | None = None
    incident_lat: float | None = Field(None, ge=-90, le=90)
    incident_lon: float | None = Field(None, ge=-180, le=180)
    incident_from: date | None = None
    incident_to: date | None = None
    narrative_language: str | None = None
    external_processing_consent: bool | None = None


class FindingAction(BaseModel):
    action: Literal["confirm", "reject", "edit"]
    value: dict | None = None


class BulkAction(BaseModel):
    ids: list[str]
    action: Literal["confirm", "reject"]


class StatedFact(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    when: str | None = None
    where: str | None = None
    who: str | None = None


class InterviewMessage(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class PackageRequest(BaseModel):
    strip_metadata: bool = False
    # The person uploaded these files from their own device, so the package normally holds only the documents
    # and the manifest's hashes let them check their copies. A copy is for someone filing from elsewhere.
    include_originals: bool = False


class FiledRequest(BaseModel):
    otp_reference: str | None = Field(None, max_length=200)


class RerunRequest(BaseModel):
    # Steps to analyse again even though they finished, e.g. after the step was improved. Failed steps
    # are always re-queued.
    agents: list[Literal["metadata", "geolocation", "visual", "audio_video", "document", "integrity"]] = []
