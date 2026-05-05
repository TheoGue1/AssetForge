# StockFlow (AssetForge) — project memory

## Last updated

- **2026-05-05** — Phase 2: SDXL `ImageGeneratorService`, bicubic `UpscalerService` (swappable backend), `run_stockflow_orchestrator` wiring metadata → base → upscale → save → CSV; integration test for real SDXL (CUDA only).

## Backend ML pipeline

- **Image request:** `ImageGenRequest` — `prompt`, `width`/`height` divisible by 8, `num_inference_steps` 1–100.
- **Base gen:** `ImageGeneratorService` — `diffusers.StableDiffusionXLPipeline` (SDXL), lazy `torch`/`diffusers` import per call, `try/except` `torch.cuda.OutOfMemoryError` → `ImageGenerationResourceError`, `finally` `del pipeline`, `gc.collect()`, `torch.cuda.empty_cache()`.
- **Upscale:** `UpscalerService` — default 2× bicubic via `torch.nn.functional.interpolate` (optional injected `upscale_backend` for Real-ESRGAN / latents later), `try/finally` cache clear.
- **Orchestrator:** `run_stockflow_orchestrator` — `MetadataService` → VRAM release → `generate_base_image` → release → `upscale_image` → save JPEG/PNG path → `append_adobe_stock_row`. Deletes PIL handles and calls `gc` / `empty_cache` between stages.
- **Metadata & CSV (Phase 1):** `AdobeStockMetadata`, `MetadataService`, `append_adobe_stock_row` unchanged in contract.
- **Tests:** Unit tests mock `diffusers` / Ollama; `pytest -m integration` runs `tests/integration/test_real_image_gen.py` (skips if no CUDA; set `STOCKFLOW_SDXL_MODEL` to override default `stabilityai/stable-diffusion-xl-base-1.0`).

## Next.js frontend

- **Current:** No Next.js app bootstrap in this repo slice; placeholder UI at `frontend/components/GenerationStudioCard.tsx` (presentation-only, controls disabled until wired).
- **Planned:** App Router, Tailwind, shadcn/ui; SSE for generation progress; Zustand or Context for queue (TBD).

## VRAM / optimization

- **Pipeline:** Unload SDXL via `del pipeline` + `gc` + `empty_cache` after each base generation; same after upscale. Orchestrator calls empty cache between LLM (CPU) and image, and before CSV.
- **Not yet:** 12–24 MP preset wiring (upscaler is 2× default); Real-ESRGAN weights.

## Next steps

1. **Phase 3 — API:** FastAPI routes, Pydantic bodies, SSE/WebSocket progress, background jobs.
2. Frontend: Next.js app + `GenerationStudioCard` + queue.
3. Optional: replace bicubic with Real-ESRGAN / latent SDXL upscaler; add `pytest` performance budget (Tier-1 suite dominated by first `diffusers` import ~5s).

## Quick links

- Backend root: `AssetForge/backend/`
- Metadata model: `backend/app/models/adobe_stock_metadata.py`
- Metadata service: `backend/app/services/metadata_service.py`
- CSV utility: `backend/app/utils/csv_manifest.py`
- Tests: `backend/tests/` — integration: `backend/tests/integration/test_real_image_gen.py`, output artifacts under `tests/integration/output/` (gitignored).
