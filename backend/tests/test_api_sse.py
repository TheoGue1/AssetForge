from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.generation_jobs import get_job_runner


class _FakeRunner:
    async def submit_job(self, payload: object) -> str:
        return "ignored"

    async def iter_events(self, job_id: str) -> AsyncIterator[dict[str, object]]:
        yield {"step": 10, "total": 30, "status": "generating", "job_id": job_id}
        yield {"step": 30, "total": 30, "status": "completed", "job_id": job_id}


@pytest.fixture()
def sse_client() -> TestClient:
    def _override_runner() -> _FakeRunner:
        return _FakeRunner()

    app.dependency_overrides[get_job_runner] = _override_runner
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_status_sse_returns_event_stream_and_payloads(sse_client: TestClient) -> None:
    with sse_client.stream("GET", "/api/status/demo-job") as response:
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type
        body = response.read().decode("utf-8")
    assert "data:" in body
    assert '"step": 10' in body or '"step": 10' in body.replace(" ", "")
    assert "generating" in body
    assert "completed" in body
