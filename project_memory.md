# StockFlow (AssetForge) — project memory

## Last updated

- **2026-05-05** — Phase 3: FastAPI `/api/generate` (202 + `job_id`), SSE `/api/status/{job_id}`, static `/api/files/{job_id}`; Next.js App Router UI (`StockFlowStudio`) with Vitest/RTL; CORS for `localhost:3000`.

## Backend ML pipeline

- **Metadata:** `AdobeStockMetadata`, `MetadataService` (Ollama JSON).
- **Image request:** `ImageGenRequest` / API `GenerateJobRequest` (dims ÷8, steps 1–100, batch size).
- **Generation:** `ImageGeneratorService` (SDXL), `UpscalerService`, `run_stock_generation_workflow` (+ optional `progress_callback` for SSE wiring).
- **Jobs:** `JobRunner` + `JobStore` — async `submit_job` schedules `asyncio.to_thread` demo pipeline or future real orchestrator; SSE subscribes via per-job queues.
- **Outputs:** Demo writes `backend/outputs/{job_id}.png`; CSV hook remains in orchestrator for full runs.

## FastAPI

- **POST `/api/generate`** — body `GenerateJobRequest`; **202** `{ "job_id": "..." }`.
- **GET `/api/status/{job_id}`** — `text/event-stream`, JSON payloads embedded in SSE `data:` lines (`step`, `total`, `status`, optional `image_urls`).
- **GET `/api/files/{job_id}`** — PNG from `backend/outputs/`.
- **CORS** — allows `http://localhost:3000`.

## Next.js frontend

- **App Router** — `app/page.tsx` renders `StockFlowStudio`.
- **Components:** `GenerationForm`, `ProgressBar`, `ImageGallery`, shadcn-style `components/ui/*`.
- **Env:** `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`); see `frontend/env.example`.
- **Tests:** `npm test` (Vitest + RTL).

## VRAM / optimization

- Sequential orchestrator stages + `torch.cuda.empty_cache()` patterns preserved from Phase 2.
- API layer never blocks on ML: returns **202** immediately; work runs in background tasks / threads.

## Next steps

1. Wire `JobRunner` `workflow_factory` to real `run_stock_generation_workflow` + disk paths / CSV.
2. WebSocket alternative or SSE reconnect handling; job persistence across restarts.
3. Replace demo PNG stub with final upscaled asset URLs.

## Quick links

- Backend root: `AssetForge/backend/` — run `uvicorn app.main:app --reload --port 8000`
- Frontend root: `AssetForge/frontend/` — run `npm run dev`
- Tests: `backend/tests/`, `frontend/components/__tests__/`
