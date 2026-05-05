import json
from unittest.mock import patch

import httpx
import pytest

from app.models.adobe_stock_metadata import AdobeStockMetadata
from app.services.metadata_service import (
    MalformedMetadataResponseError,
    MetadataService,
    OllamaTransportError,
)


def _sample_payload() -> dict:
    return {
        "title": "Studio wine glass on white background",
        "keywords": [f"keyword{i}" for i in range(50)],
        "category": 1057,
        "releases": "",
    }


def test_generate_metadata_happy_path_mocks_ollama_chat() -> None:
    payload = _sample_payload()
    fake_response = {"message": {"content": json.dumps(payload)}}

    with patch("app.services.metadata_service.ollama.chat", return_value=fake_response):
        svc = MetadataService(model="dummy-model")
        result = svc.generate_metadata("wine glass on white")

    assert isinstance(result, AdobeStockMetadata)
    assert result.title == payload["title"]
    assert len(result.keywords) == 50
    assert result.category == 1057


def test_malformed_then_valid_retries_and_succeeds() -> None:
    payload = _sample_payload()
    responses = [
        {"message": {"content": "NOT JSON AT ALL"}},
        {"message": {"content": json.dumps(payload)}},
    ]

    with patch(
        "app.services.metadata_service.ollama.chat",
        side_effect=responses,
    ):
        svc = MetadataService(model="dummy-model", max_parse_attempts=2)
        result = svc.generate_metadata("subject prompt")

    assert result.title == payload["title"]


def test_repeated_malformed_raises_specific_error() -> None:
    bad = {"message": {"content": "still not json"}}

    with patch(
        "app.services.metadata_service.ollama.chat",
        return_value=bad,
    ):
        svc = MetadataService(model="dummy-model", max_parse_attempts=2)

        with pytest.raises(MalformedMetadataResponseError):
            svc.generate_metadata("x")


def test_ollama_timeout_raises_transport_error() -> None:
    with patch(
        "app.services.metadata_service.ollama.chat",
        side_effect=httpx.TimeoutException("timed out"),
    ):
        svc = MetadataService(model="dummy-model")

        with pytest.raises(OllamaTransportError):
            svc.generate_metadata("y")


def test_ollama_connection_error_raises_transport_error() -> None:
    with patch(
        "app.services.metadata_service.ollama.chat",
        side_effect=httpx.ConnectError("connection refused"),
    ):
        svc = MetadataService(model="dummy-model")

        with pytest.raises(OllamaTransportError):
            svc.generate_metadata("z")
