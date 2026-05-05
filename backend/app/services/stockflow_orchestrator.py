from __future__ import annotations

import gc
from pathlib import Path

from app.models.image_gen_request import ImageGenRequest
from app.services.image_generator_service import ImageGeneratorService
from app.services.metadata_service import MetadataService
from app.services.upscaler_service import UpscalerService
from app.utils.csv_manifest import append_adobe_stock_row


def _release_between_ml_stages() -> None:
    import torch

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def run_stock_generation_workflow(
    *,
    subject_prompt: str,
    image_request: ImageGenRequest,
    image_filename: str,
    output_image_path: Path,
    csv_path: Path,
    metadata_service: MetadataService,
    image_service: ImageGeneratorService,
    upscaler: UpscalerService,
) -> Path:
    """Run metadata → SDXL base → upscale → save → CSV, clearing VRAM between heavy stages."""

    metadata = metadata_service.generate_metadata(subject_prompt)
    _release_between_ml_stages()

    base_image = image_service.generate_base_image(image_request)
    _release_between_ml_stages()

    final_image = upscaler.upscale_image(base_image)
    _release_between_ml_stages()

    output_image_path.parent.mkdir(parents=True, exist_ok=True)
    final_image.save(output_image_path)

    append_adobe_stock_row(csv_path, image_filename, metadata)

    del base_image
    del final_image
    del metadata
    _release_between_ml_stages()

    return output_image_path
