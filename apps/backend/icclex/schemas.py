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
    # Set when the statement is about one file, such as how the submitter obtained it.
    evidence_id: str | None = None
    when: str | None = None
    where: str | None = None
    who: str | None = None


class InterviewMessage(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class PackageRequest(BaseModel):
    # Files go to OTPLink as uploaded, hidden details included; the person has to agree to that.
    consent_files_as_they_are: bool = False


class FiledRequest(BaseModel):
    otp_reference: str | None = Field(None, max_length=200)


class RerunRequest(BaseModel):
    # Steps to analyse again even though they finished, e.g. after the step was improved. Failed steps
    # are always re-queued.
    agents: list[Literal["metadata", "geolocation", "visual", "audio_video", "document", "integrity"]] = []
