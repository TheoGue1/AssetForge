/**
 * Presentation-only shell for StockFlow generation controls (subject, resolution presets).
 * Wire to global store only when the parent passes callbacks or uses an existing provider.
 */
export function GenerationStudioCard() {
  return (
    <section
      className="rounded-xl border border-zinc-800 bg-zinc-950 p-6 text-zinc-100 shadow-xl shadow-black/40"
      aria-labelledby="generation-studio-heading"
    >
      <h2
        id="generation-studio-heading"
        className="text-lg font-semibold tracking-tight text-zinc-50"
      >
        StockFlow · Studio generation
      </h2>
      <p className="mt-2 max-w-prose text-sm text-zinc-400">
        Configure subject and export presets. Backend endpoints will attach here in Phase 2
        (diffusers pipeline + SSE progress).
      </p>
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm">
          <span className="font-medium text-zinc-300">Subject brief</span>
          <input
            type="text"
            name="subject"
            placeholder="e.g., ripe strawberry on pure white"
            className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none ring-offset-zinc-950 placeholder:text-zinc-600 focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700"
            disabled
            readOnly
          />
        </label>
        <label className="flex flex-col gap-2 text-sm">
          <span className="font-medium text-zinc-300">Resolution preset</span>
          <select
            name="resolution"
            className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none ring-offset-zinc-950 focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700"
            disabled
            defaultValue="preview"
          >
            <option value="preview">Preview (fast)</option>
            <option value="stock">Stock / upscaled</option>
          </select>
        </label>
      </div>
    </section>
  );
}
