from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.services.generation_jobs import JobRunner, JobStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = JobStore()
    app.state.job_runner = JobRunner(store)
    yield


app = FastAPI(title="StockFlow API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
