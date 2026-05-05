import pytest
from pydantic import ValidationError

from app.models.adobe_stock_metadata import AdobeStockMetadata


def _valid_keywords() -> list[str]:
    return [f"kw{i}" for i in range(50)]


def test_accepts_valid_title_and_exactly_fifty_keywords() -> None:
    meta = AdobeStockMetadata(
        title="Fresh strawberry isolated on white studio background",
        keywords=_valid_keywords(),
        category=1056,
        releases="",
    )
    assert len(meta.title) < 200
    assert len(meta.keywords) == 50


def test_rejects_title_over_200_characters() -> None:
    long_title = "x" * 201
    with pytest.raises(ValidationError) as exc:
        AdobeStockMetadata(
            title=long_title,
            keywords=_valid_keywords(),
            category=1,
        )
    errs = exc.value.errors()
    assert any(e["type"] == "string_too_long" for e in errs)


def test_rejects_fewer_than_fifty_keywords() -> None:
    with pytest.raises(ValidationError) as exc:
        AdobeStockMetadata(
            title="Valid title",
            keywords=[f"k{i}" for i in range(49)],
            category=1,
        )
    errs = exc.value.errors()
    assert any(
        e.get("ctx", {}).get("min_length") == 50 or "keywords" in str(e.get("loc", ()))
        for e in errs
    )


def test_rejects_more_than_fifty_keywords() -> None:
    with pytest.raises(ValidationError) as exc:
        AdobeStockMetadata(
            title="Valid title",
            keywords=[f"k{i}" for i in range(51)],
            category=1,
        )
    errs = exc.value.errors()
    assert any(
        e.get("ctx", {}).get("max_length") == 50 or "keywords" in str(e.get("loc", ()))
        for e in errs
    )
