# StockFlow (AssetForge) — project memory

## Last updated

- **2026-05-05** — Phase 1 backend: Pydantic metadata, Ollama metadata service (mocked in tests), CSV manifest.

## Backend ML pipeline

- **Current:** No diffusion pipeline yet (Phase 2). Metadata path only.
- **Models (planned):** Local SDXL/Cascade via `diffusers`; local LLM via Ollama for JSON metadata.
- **Implemented:**
  - `AdobeStockMetadata` — `title` ≤200 chars; **exactly** 50 keywords; integer `category`; optional `releases`.
  - `MetadataService.generate_metadata` — `ollama.chat` with a strict JSON-only system prompt; retries parse/validation up to `max_parse_attempts`; raises `MalformedMetadataResponseError` or `OllamaTransportError` (no real Ollama in unit tests — fully mocked).
  - `append_adobe_stock_row` — writes headers `Filename,Title,Keywords,Category,Releases` once; appends rows; `csv` module quotes fields (commas in titles).

## Next.js frontend

- **Current:** No Next.js app bootstrap in this repo slice; placeholder UI at `frontend/components/GenerationStudioCard.tsx` (presentation-only, controls disabled until wired).
- **Planned:** App Router, Tailwind, shadcn/ui; SSE for generation progress; Zustand or Context for queue (TBD).

## VRAM / optimization

- **Planned:** Sequential load — LLM → unload → diffusion → unload → upscale; explicit `torch.cuda.empty_cache()` in services (not applicable until Phase 2).

## Next steps

1. **Phase 2 — Image generation:** TDD `ImageGenerationService` with mocked `diffusers` pipelines; resolution presets (preview vs upscaled 12–24 MP path); VRAM-safe sequencing per workspace rules.
2. FastAPI routes: metadata generation, CSV export path, generation job + SSE.
3. Scaffold Next.js app in `AssetForge/frontend` and connect `GenerationStudioCard` to APIs.

## Quick links

- Backend root: `AssetForge/backend/`
- Metadata model: `backend/app/models/adobe_stock_metadata.py`
- Metadata service: `backend/app/services/metadata_service.py`
- CSV utility: `backend/app/utils/csv_manifest.py`
- Tests: `backend/tests/`
