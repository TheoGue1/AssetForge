from __future__ import annotations

import gc
from typing import Any

from PIL import Image

from app.models.image_gen_request import ImageGenRequest


class ImageGenerationError(Exception):
    """Base error for image generation failures (maps cleanly to HTTP responses)."""


class ImageGenerationResourceError(ImageGenerationError):
    """Insufficient GPU memory or similar resource exhaustion."""


class ImageGeneratorService:
    """SDXL base generation with explicit VRAM cleanup after each call."""

    def __init__(
        self,
        model_id: str,
        *,
        device: str | None = None,
        torch_dtype: str = "float16",
        variant: str | None = "fp16",
    ) -> None:
        self._model_id = model_id
        self._device_arg = device
        self._torch_dtype_name = torch_dtype
        self._variant = variant

    def generate_base_image(self, request: ImageGenRequest) -> Image.Image:
        import torch
        from diffusers import StableDiffusionXLPipeline

        device = (
            self._device_arg
            if self._device_arg is not None
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        dtype_map = {
            "float16": torch.float16,
            "float32": torch.float32,
            "bfloat16": torch.bfloat16,
        }
        torch_dtype = dtype_map.get(self._torch_dtype_name, torch.float16)

        pipeline: Any = None
        try:
            extra: dict[str, Any] = {
                "torch_dtype": torch_dtype,
                "use_safetensors": True,
            }
            if self._variant is not None:
                extra["variant"] = self._variant

            pipeline = StableDiffusionXLPipeline.from_pretrained(self._model_id, **extra)
            pipeline = pipeline.to(device)

            result = pipeline(
                prompt=request.prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
            )
            image = result.images[0]
            if not isinstance(image, Image.Image):
                msg = "Pipeline returned a non-PIL image"
                raise ImageGenerationError(msg)
            return image
        except torch.cuda.OutOfMemoryError as exc:
            self._release_gpu_memory()
            raise ImageGenerationResourceError(
                "Image generation failed: GPU ran out of memory. "
                "Try a smaller resolution or fewer concurrent jobs."
            ) from exc
        finally:
            if pipeline is not None:
                del pipeline
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _release_gpu_memory(self) -> None:
        import torch

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
