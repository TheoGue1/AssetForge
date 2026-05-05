from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas.generation import GenerateJobAccepted, GenerateJobRequest
from app.services.generation_jobs import JobRunner, _outputs_root, get_job_runner

router = APIRouter(prefix="/api")


@router.post("/generate", status_code=202, response_model=GenerateJobAccepted)
async def enqueue_generation(
    payload: GenerateJobRequest,
    runner: Annotated[JobRunner, Depends(get_job_runner)],
) -> GenerateJobAccepted:
    job_id = await runner.submit_job(payload)
    return GenerateJobAccepted(job_id=job_id)


@router.get("/status/{job_id}")
async def stream_generation_status(
    job_id: str,
    runner: Annotated[JobRunner, Depends(get_job_runner)],
) -> StreamingResponse:
    async def byte_stream() -> AsyncIterator[bytes]:
        async for payload in runner.iter_events(job_id):
            yield f"data: {json.dumps(payload)}\n\n".encode("utf-8")

    return StreamingResponse(byte_stream(), media_type="text/event-stream")


@router.get("/files/{job_id}")
async def download_job_image(job_id: str) -> FileResponse:
    path = _outputs_root() / f"{job_id}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Output not found")
    return FileResponse(path, media_type="image/png")
