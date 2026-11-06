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


class FiledRequest(BaseModel):
    otp_reference: str | None = Field(None, max_length=200)
