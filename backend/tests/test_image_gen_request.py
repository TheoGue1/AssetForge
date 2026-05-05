import pytest
from pydantic import ValidationError

from app.models.image_gen_request import ImageGenRequest


def test_accepts_valid_dimensions_divisible_by_8_and_steps_in_bounds() -> None:
    req = ImageGenRequest(
        prompt="a red apple on white background",
        width=512,
        height=512,
        num_inference_steps=25,
    )
    assert req.width % 8 == 0
    assert req.height % 8 == 0
    assert 1 <= req.num_inference_steps <= 100


def test_rejects_width_not_divisible_by_8() -> None:
    with pytest.raises(ValidationError) as exc:
        ImageGenRequest(
            prompt="x",
            width=511,
            height=512,
            num_inference_steps=10,
        )
    assert any("8" in str(e.get("msg", "")) for e in exc.value.errors())


def test_rejects_height_not_divisible_by_8() -> None:
    with pytest.raises(ValidationError):
        ImageGenRequest(
            prompt="x",
            width=512,
            height=518,
            num_inference_steps=10,
        )


def test_rejects_num_inference_steps_below_one() -> None:
    with pytest.raises(ValidationError):
        ImageGenRequest(
            prompt="x",
            width=512,
            height=512,
            num_inference_steps=0,
        )


def test_rejects_num_inference_steps_above_100() -> None:
    with pytest.raises(ValidationError):
        ImageGenRequest(
            prompt="x",
            width=512,
            height=512,
            num_inference_steps=101,
        )
