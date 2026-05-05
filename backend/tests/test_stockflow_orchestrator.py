from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

from app.models.adobe_stock_metadata import AdobeStockMetadata
from app.models.image_gen_request import ImageGenRequest
from app.services.image_generator_service import ImageGeneratorService
from app.services.metadata_service import MetadataService
from app.services.stockflow_orchestrator import run_stock_generation_workflow
from app.services.upscaler_service import UpscalerService


def _metadata() -> AdobeStockMetadata:
    return AdobeStockMetadata(
        title="Red apple isolated on white studio background",
        keywords=[f"keyword{i}" for i in range(50)],
        category=1056,
        releases="",
    )


def _image_request() -> ImageGenRequest:
    return ImageGenRequest(
        prompt="a red apple on white background",
        width=512,
        height=512,
        num_inference_steps=2,
    )


def test_orchestrator_calls_pipeline_saves_image_and_appends_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "adobe_stock_upload.csv"
    image_path = tmp_path / "export_001.jpg"

    meta = _metadata()
    metadata_service = MagicMock(spec=MetadataService)
    metadata_service.generate_metadata.return_value = meta

    base = Image.new("RGB", (512, 512), color=(200, 0, 0))
    image_service = MagicMock(spec=ImageGeneratorService)
    image_service.generate_base_image.return_value = base

    upscaled = Image.new("RGB", (1024, 1024), color=(220, 10, 10))
    upscaler = MagicMock(spec=UpscalerService)
    upscaler.upscale_image.return_value = upscaled

    run_stock_generation_workflow(
        subject_prompt="studio apple on white",
        image_request=_image_request(),
        image_filename="export_001.jpg",
        output_image_path=image_path,
        csv_path=csv_path,
        metadata_service=metadata_service,
        image_service=image_service,
        upscaler=upscaler,
    )

    metadata_service.generate_metadata.assert_called_once_with("studio apple on white")
    image_service.generate_base_image.assert_called_once()
    upscaler.upscale_image.assert_called_once()

    assert image_path.exists()
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["Filename", "Title", "Keywords", "Category", "Releases"]
    assert rows[1][0] == "export_001.jpg"


def test_orchestrator_call_order_metadata_before_image_before_upscale(
    tmp_path: Path,
) -> None:
    """Ensure orchestration order: metadata → base image → upscale."""

    calls: list[str] = []
    meta = _metadata()

    metadata_service = MagicMock(spec=MetadataService)

    def _meta_side_effect(prompt: str) -> AdobeStockMetadata:
        calls.append("metadata")
        assert prompt == "x"
        return meta

    metadata_service.generate_metadata.side_effect = _meta_side_effect

    image_service = MagicMock(spec=ImageGeneratorService)

    def _img_side_effect(req: ImageGenRequest) -> Image.Image:
        calls.append("image")
        return Image.new("RGB", (req.width, req.height))

    image_service.generate_base_image.side_effect = _img_side_effect

    upscaler = MagicMock(spec=UpscalerService)

    def _up_side_effect(img: Image.Image) -> Image.Image:
        calls.append("upscale")
        return Image.new("RGB", (img.size[0] * 2, img.size[1] * 2))

    upscaler.upscale_image.side_effect = _up_side_effect

    out = tmp_path / "o.jpg"
    run_stock_generation_workflow(
        subject_prompt="x",
        image_request=_image_request(),
        image_filename="o.jpg",
        output_image_path=out,
        csv_path=tmp_path / "c.csv",
        metadata_service=metadata_service,
        image_service=image_service,
        upscaler=upscaler,
    )

    assert calls == ["metadata", "image", "upscale"]
    assert out.exists()
