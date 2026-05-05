from __future__ import annotations

import csv
from pathlib import Path

from app.models.adobe_stock_metadata import AdobeStockMetadata

HEADERS: tuple[str, ...] = (
    "Filename",
    "Title",
    "Keywords",
    "Category",
    "Releases",
)


def append_adobe_stock_row(
    csv_path: Path,
    filename: str,
    metadata: AdobeStockMetadata,
) -> None:
    """Append one Adobe Stock contributor row; write headers if the file is new."""

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow(HEADERS)
        writer.writerow(
            [
                filename,
                metadata.title,
                ", ".join(metadata.keywords),
                str(metadata.category),
                metadata.releases,
            ],
        )
