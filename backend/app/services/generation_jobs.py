from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import Request
from PIL import Image

from app.models.image_gen_request import ImageGenRequest
from app.schemas.generation import GenerateJobRequest


def _outputs_root() -> Path:
    return Path(__file__).resolve().parents[2] / "outputs"


@dataclass
class JobRecord:
    job_id: str
    step: int = 0
    total: int = 30
    status: str = "queued"
    image_urls: list[str] = field(default_factory=list)
    error: str | None = None


class JobStore:
    """In-memory job registry + subscription queues for SSE."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._listeners: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}

    def create(self, job_id: str) -> JobRecord:
        record = JobRecord(job_id=job_id)
        self._jobs[job_id] = record
        self._listeners.setdefault(job_id, [])
        return record

    def has(self, job_id: str) -> bool:
        return job_id in self._jobs

    def emit(self, job_id: str, data: dict[str, Any]) -> None:
        job = self._jobs[job_id]
        if "step" in data:
            job.step = int(data["step"])
        if "total" in data:
            job.total = int(data["total"])
        if "status" in data:
            job.status = str(data["status"])
        if "image_urls" in data:
            job.image_urls = list(data["image_urls"])
        if "error" in data and data["error"] is not None:
            job.error = str(data["error"])

        snapshot = self.snapshot(job_id)
        for queue in list(self._listeners.get(job_id, [])):
            queue.put_nowait(snapshot)

    def snapshot(self, job_id: str) -> dict[str, Any]:
        job = self._jobs[job_id]
        payload: dict[str, Any] = {
            "job_id": job.job_id,
            "step": job.step,
            "total": job.total,
            "status": job.status,
        }
        if job.image_urls:
            payload["image_urls"] = job.image_urls
        if job.error:
            payload["error"] = job.error
        return payload

    def subscribe(self, job_id: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._listeners.setdefault(job_id, []).append(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        listeners = self._listeners.get(job_id, [])
        if queue in listeners:
            listeners.remove(queue)


class JobRunner:
    """Queues generation work without blocking request handlers."""

    def __init__(
        self,
        store: JobStore,
        *,
        workflow_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._store = store
        self._workflow_factory = workflow_factory

    async def submit_job(self, payload: GenerateJobRequest) -> str:
        job_id = str(uuid.uuid4())
        self._store.create(job_id)
        self._store.emit(job_id, {"step": 0, "total": 30, "status": "queued"})
        asyncio.create_task(self._execute(job_id, payload))
        return job_id

    async def _execute(self, job_id: str, payload: GenerateJobRequest) -> None:
        try:
            await self._run_pipeline(job_id, payload)
        except Exception as exc:  # noqa: BLE001
            self._store.emit(
                job_id,
                {
                    "step": 0,
                    "total": 30,
                    "status": "failed",
                    "error": str(exc),
                },
            )

    async def _run_pipeline(self, job_id: str, payload: GenerateJobRequest) -> None:
        def progress(event: dict[str, Any]) -> None:
            self._store.emit(job_id, event)

        await asyncio.to_thread(
            self._blocking_run,
            job_id,
            payload,
            progress,
        )

    def _blocking_run(
        self,
        job_id: str,
        payload: GenerateJobRequest,
        progress: Callable[[dict[str, Any]], None],
    ) -> None:
        if self._workflow_factory is not None:
            self._workflow_factory(job_id, payload, progress)
            return
        self._demo_run(job_id, payload, progress)

    def _demo_run(
        self,
        job_id: str,
        payload: GenerateJobRequest,
        progress: Callable[[dict[str, Any]], None],
    ) -> None:
        """Deterministic stand-in so API/SSE work without loading ML models."""

        _ = payload
        progress({"step": 5, "total": 30, "status": "metadata"})
        progress({"step": 15, "total": 30, "status": "generating"})
        progress({"step": 25, "total": 30, "status": "upscaling"})
        _outputs_root().mkdir(parents=True, exist_ok=True)
        placeholder = _outputs_root() / f"{job_id}.png"
        Image.new("RGB", (64, 64), color=(240, 240, 240)).save(placeholder, format="PNG")
        url_path = f"/api/files/{job_id}"
        progress(
            {
                "step": 30,
                "total": 30,
                "status": "completed",
                "image_urls": [url_path],
            },
        )

    async def iter_events(self, job_id: str) -> AsyncIterator[dict[str, Any]]:
        if not self._store.has(job_id):
            yield {"job_id": job_id, "step": 0, "total": 30, "status": "not_found"}
            return

        snapshot = self._store.snapshot(job_id)
        if snapshot.get("status") in {"completed", "failed"}:
            yield snapshot
            return

        queue = self._store.subscribe(job_id)
        try:
            yield snapshot
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=300.0)
                yield event
                if event.get("status") in {"completed", "failed"}:
                    break
        finally:
            self._store.unsubscribe(job_id, queue)


def get_job_runner(request: Request) -> JobRunner:
    return request.app.state.job_runner


def build_default_image_request(payload: GenerateJobRequest) -> ImageGenRequest:
    prompt = (
        f"{payload.subject}. {payload.prompt}. Background: {payload.background}."
    ).strip()
    return ImageGenRequest(
        prompt=prompt,
        width=payload.width,
        height=payload.height,
        num_inference_steps=payload.num_inference_steps,
    )
