from __future__ import annotations

import gc
from collections.abc import Callable

from PIL import Image


def _default_bicubic_upscale(image: Image.Image, scale: int) -> Image.Image:
    """Reference 2D upscale (bicubic) used when no external ESRGAN weights are configured."""

    import numpy as np
    import torch
    import torch.nn.functional as F

    arr = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
    if torch.cuda.is_available():
        tensor = tensor.to(device="cuda", dtype=torch.float32)
    else:
        tensor = tensor.to(dtype=torch.float32)
    _b, _c, h, w = tensor.shape
    upscaled = F.interpolate(
        tensor,
        size=(h * scale, w * scale),
        mode="bicubic",
        align_corners=False,
    )
    upscaled = upscaled.detach().float().cpu()
    out = (upscaled.squeeze(0).permute(1, 2, 0).clamp(0.0, 1.0) * 255.0).byte().numpy()
    return Image.fromarray(out, mode="RGB")


class UpscalerService:
    """Image upscale step with explicit GPU cache cleanup after each call."""

    def __init__(
        self,
        scale_factor: int = 2,
        *,
        upscale_backend: Callable[[Image.Image, int], Image.Image] | None = None,
    ) -> None:
        self._scale_factor = max(1, scale_factor)
        self._backend = upscale_backend or _default_bicubic_upscale

    def upscale_image(self, image: Image.Image) -> Image.Image:
        try:
            return self._backend(image, self._scale_factor)
        finally:
            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
