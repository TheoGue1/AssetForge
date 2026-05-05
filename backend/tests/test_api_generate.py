from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.generation_jobs import JobRunner, get_job_runner


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    mock_runner = AsyncMock(spec=JobRunner)
    mock_runner.submit_job.return_value = "test-job-id"

    def _override_runner() -> JobRunner:
        return mock_runner

    app.dependency_overrides[get_job_runner] = _override_runner
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_generate_returns_202_and_job_id(client: TestClient) -> None:
    payload = {
        "prompt": "studio lighting",
        "subject": "red apple",
        "background": "pure white",
        "batch_size": 1,
        "width": 512,
        "height": 512,
        "num_inference_steps": 20,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["job_id"] == "test-job-id"


def test_post_generate_invalid_width_returns_422(client: TestClient) -> None:
    payload = {
        "prompt": "studio lighting",
        "subject": "red apple",
        "background": "pure white",
        "batch_size": 1,
        "width": 511,
        "height": 512,
        "num_inference_steps": 20,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422
