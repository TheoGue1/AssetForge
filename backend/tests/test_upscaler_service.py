from __future__ import annotations

from unittest.mock import MagicMock, patch

import torch
from PIL import Image

from app.services.upscaler_service import UpscalerService


def test_upscale_image_returns_scaled_dimensions_with_mocked_backend() -> None:
    inp = Image.new("RGB", (64, 48), color=(10, 20, 30))
    expected = Image.new("RGB", (128, 96), color=(50, 60, 70))

    mock_backend = MagicMock(return_value=expected)
    svc = UpscalerService(scale_factor=2, upscale_backend=mock_backend)

    out = svc.upscale_image(inp)

    assert out is expected
    assert out.size == (inp.size[0] * 2, inp.size[1] * 2)
    mock_backend.assert_called_once_with(inp, 2)


@patch("torch.cuda.is_available", return_value=True)
@patch("torch.cuda.empty_cache")
@patch("gc.collect")
def test_upscale_runs_cleanup_in_finally(
    mock_gc: MagicMock,
    mock_empty_cache: MagicMock,
    _is_cuda: MagicMock,
) -> None:
    inp = Image.new("RGB", (8, 8), color="white")
    mock_impl = MagicMock(return_value=Image.new("RGB", (16, 16), color="white"))
    svc = UpscalerService(scale_factor=2, upscale_backend=mock_impl)
    svc.upscale_image(inp)

    mock_gc.assert_called()
    mock_empty_cache.assert_called()
