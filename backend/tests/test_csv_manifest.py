import csv
from pathlib import Path

from app.models.adobe_stock_metadata import AdobeStockMetadata
from app.utils.csv_manifest import append_adobe_stock_row


def _keywords50() -> list[str]:
    return [f"kw{i}" for i in range(50)]


def _meta(title: str = "Title") -> AdobeStockMetadata:
    return AdobeStockMetadata(
        title=title,
        keywords=_keywords50(),
        category=1056,
        releases="",
    )


def test_writes_headers_when_file_does_not_exist(tmp_path: Path) -> None:
    path = tmp_path / "adobe_stock_upload.csv"
    append_adobe_stock_row(path, "shot001.jpg", _meta())

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "Filename,Title,Keywords,Category,Releases"
    assert "shot001.jpg" in lines[1]


def test_appends_without_duplicating_headers(tmp_path: Path) -> None:
    path = tmp_path / "adobe_stock_upload.csv"
    append_adobe_stock_row(path, "a.jpg", _meta(title="One"))
    append_adobe_stock_row(path, "b.jpg", _meta(title="Two"))

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["Filename", "Title", "Keywords", "Category", "Releases"]
    assert rows[1][0] == "a.jpg"
    assert rows[1][1] == "One"
    assert rows[2][0] == "b.jpg"
    assert rows[2][1] == "Two"


def test_title_with_comma_is_escaped_and_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "adobe_stock_upload.csv"
    title = "Strawberry, ripe and isolated on white"
    append_adobe_stock_row(path, "berry.jpg", _meta(title=title))

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[1][1] == title
