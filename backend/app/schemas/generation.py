from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class GenerateJobRequest(BaseModel):
    """API payload to enqueue a StockFlow generation job."""

    prompt: Annotated[str, Field(min_length=1, max_length=2000)]
    subject: Annotated[str, Field(min_length=1, max_length=500)]
    background: Annotated[str, Field(min_length=1, max_length=500)]
    batch_size: Annotated[int, Field(ge=1, le=16)]
    width: int
    height: int
    num_inference_steps: Annotated[int, Field(ge=1, le=100)]

    @field_validator("width", "height")
    @classmethod
    def dimensions_divisible_by_8(cls, value: int) -> int:
        if value % 8 != 0:
            msg = "width and height must be divisible by 8 (Stable Diffusion requirement)"
            raise ValueError(msg)
        return value


class GenerateJobAccepted(BaseModel):
    job_id: str
