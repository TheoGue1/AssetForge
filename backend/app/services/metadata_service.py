from __future__ import annotations

import json
import re
from typing import Any

import httpx
import ollama
from pydantic import ValidationError

from app.models.adobe_stock_metadata import AdobeStockMetadata

ADOBE_STOCK_JSON_SYSTEM = """You are an Adobe Stock contributor SEO expert. The user will \
describe a stock image. Respond with ONE JSON object only—no markdown fences, no commentary, \
no text before or after the JSON.

The JSON must match this exact shape and constraints:
- "title": string, 1–200 characters, professional, Title Case, no brand names unless generic, \
describe the subject and "isolated on white" or similar when applicable.
- "keywords": array of EXACTLY 50 distinct English strings, ordered from most to least \
relevant, no duplicates, no empty strings, suitable for microstock search.
- "category": integer, a plausible Adobe Stock category id for the subject.
- "releases": string; use an empty string "" when there are no model or property releases.

Output valid minified or pretty JSON; it must be parseable with json.loads as a single object."""


class MetadataGenerationError(Exception):
    """Base class for metadata generation failures."""


class MalformedMetadataResponseError(MetadataGenerationError):
    """LLM output could not be parsed or did not validate after all attempts."""


class OllamaTransportError(MetadataGenerationError):
    """Network or transport failure when calling the local Ollama API."""


def _parse_json_object_from_llm(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            count=1,
            flags=re.IGNORECASE,
        )
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()
    return json.loads(text)


class MetadataService:
    """Generates `AdobeStockMetadata` via a local Ollama chat model (JSON-only)."""

    def __init__(
        self,
        model: str,
        max_parse_attempts: int = 2,
    ) -> None:
        self._model = model
        self._max_parse_attempts = max(1, max_parse_attempts)

    @property
    def model(self) -> str:
        return self._model

    def generate_metadata(self, prompt: str) -> AdobeStockMetadata:
        last_error: Exception | None = None

        for _ in range(self._max_parse_attempts):
            try:
                response = ollama.chat(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": ADOBE_STOCK_JSON_SYSTEM},
                        {
                            "role": "user",
                            "content": (
                                "Image brief for metadata (title, 50 keywords, category, "
                                f'releases as ""): {prompt}'
                            ),
                        },
                    ],
                )
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                raise OllamaTransportError(str(exc)) from exc
            except httpx.HTTPError as exc:
                raise OllamaTransportError(str(exc)) from exc

            content = response["message"]["content"]
            try:
                data = _parse_json_object_from_llm(content)
                return AdobeStockMetadata.model_validate(data)
            except (json.JSONDecodeError, ValidationError, KeyError, TypeError) as exc:
                last_error = exc
                continue

        raise MalformedMetadataResponseError(
            "Could not obtain valid Adobe Stock metadata JSON from the LLM."
        ) from last_error
