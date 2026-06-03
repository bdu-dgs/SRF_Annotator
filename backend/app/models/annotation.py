from typing import Literal

from pydantic import BaseModel, Field


ReviewerStatus = Literal["correct", "false"]


class AnnotationResult(BaseModel):
    note_id: str = Field(..., description="Clinical note identifier from the CSV.")
    srf_present: bool = Field(..., description="Whether any social risk factor is present.")
    srf_type: str | None = Field(
        default=None,
        description="Detected social risk factor category, or null if none is present.",
    )
    supporting_phrase: str | None = Field(
        default=None,
        description="Exact evidence phrase copied from the note, or null if none is present.",
    )
    reviewer_status: ReviewerStatus | None = Field(
        default=None,
        description="Human reviewer mark after reviewing the LLM annotation.",
    )


class AnnotationBatchResponse(BaseModel):
    results: list[AnnotationResult]


class SaveAnnotationsRequest(BaseModel):
    annotations: list[AnnotationResult]
