from unittest.mock import MagicMock, patch

import pytest
import torch
from PIL import Image

from app.models.image_gen_request import ImageGenRequest
from app.services.image_generator_service import (
    ImageGenerationResourceError,
    ImageGeneratorService,
)


def _request() -> ImageGenRequest:
    return ImageGenRequest(
        prompt="a red apple on white background",
        width=512,
        height=512,
        num_inference_steps=2,
    )


@patch("diffusers.StableDiffusionXLPipeline")
def test_generate_base_image_returns_pil_from_mocked_pipeline(
    mock_pipeline_cls: MagicMock,
) -> None:
    dummy = Image.new("RGB", (512, 512), color=(200, 10, 10))
    mock_pipe = MagicMock()
    mock_out = MagicMock()
    mock_out.images = [dummy]
    mock_pipe.return_value = mock_out
    mock_pipe.to.return_value = mock_pipe
    mock_pipeline_cls.from_pretrained.return_value = mock_pipe

    svc = ImageGeneratorService(
        model_id="test/model",
        device="cpu",
        torch_dtype="float32",
        variant=None,
    )
    out = svc.generate_base_image(_request())

    assert isinstance(out, Image.Image)
    assert out.size == (512, 512)
    mock_pipe.assert_called_once()
    mock_pipeline_cls.from_pretrained.assert_called_once()


@patch("torch.cuda.is_available", return_value=True)
@patch("torch.cuda.empty_cache")
@patch("app.services.image_generator_service.gc.collect")
@patch("diffusers.StableDiffusionXLPipeline")
def test_out_of_memory_clears_cache_and_raises_resource_error(
    mock_pipeline_cls: MagicMock,
    mock_gc: MagicMock,
    mock_empty_cache: MagicMock,
    _cuda_available: MagicMock,
) -> None:
    mock_pipe = MagicMock()
    mock_pipe.to.return_value = mock_pipe
    mock_pipe.side_effect = torch.cuda.OutOfMemoryError("simulated OOM")
    mock_pipeline_cls.from_pretrained.return_value = mock_pipe

    svc = ImageGeneratorService(
        model_id="test/model",
        device="cpu",
        torch_dtype="float32",
        variant=None,
    )

    with pytest.raises(ImageGenerationResourceError) as exc_info:
        svc.generate_base_image(_request())

    assert "memory" in str(exc_info.value).lower() or "GPU" in str(exc_info.value)
    mock_empty_cache.assert_called()
    mock_gc.assert_called()
