from __future__ import annotations

import os
from pathlib import Path

import pytest
import torch
from PIL import Image

from app.models.image_gen_request import ImageGenRequest
from app.services.image_generator_service import ImageGeneratorService

_OUTPUT_DIR = Path(__file__).resolve().parent / "output"


@pytest.mark.integration
def test_real_sdxl_generates_low_res_image() -> None:
    if not torch.cuda.is_available():
        pytest.skip("CUDA is required for the real SDXL integration proof test")

    model_id = os.environ.get(
        "STOCKFLOW_SDXL_MODEL",
        "stabilityai/stable-diffusion-xl-base-1.0",
    )

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    svc = ImageGeneratorService(
        model_id=model_id,
        device="cuda",
        torch_dtype="float16",
        variant="fp16",
    )
    req = ImageGenRequest(
        prompt="a red apple on white background",
        width=512,
        height=512,
        num_inference_steps=40,
    )

    image = svc.generate_base_image(req)

    assert isinstance(image, Image.Image)
    assert image.size == (req.width, req.height)

    dest = _OUTPUT_DIR / "integration_low_res_proof.png"
    image.save(dest)
    assert dest.exists()
