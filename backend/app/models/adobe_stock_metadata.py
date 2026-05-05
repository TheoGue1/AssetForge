from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class AdobeStockMetadata(BaseModel):
    """Strict Adobe Stock row metadata validated before CSV export."""

    title: Annotated[str, Field(max_length=200)]
    keywords: Annotated[list[str], Field(min_length=50, max_length=50)]
    category: int
    releases: str = ""
