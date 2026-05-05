"use client";

import { useCallback, useState } from "react";

import { GenerationForm, type GenerationFormValues } from "@/components/GenerationForm";
import { ImageGallery, type GalleryImage } from "@/components/ImageGallery";
import { ProgressBar } from "@/components/ProgressBar";
import { apiBaseUrl } from "@/lib/api";

export function StockFlowStudio() {
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(30);
  const [statusLabel, setStatusLabel] = useState<string>("Idle");
  const [images, setImages] = useState<GalleryImage[]>([]);

  const handleSubmit = useCallback((values: GenerationFormValues) => {
    setImages([]);
    setCurrentStep(0);
    setTotalSteps(30);
    setStatusLabel("Queued");

    void (async () => {
      const response = await fetch(`${apiBaseUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: values.prompt,
          subject: values.subject,
          background: values.background,
          batch_size: values.batchSize,
          width: values.width,
          height: values.height,
          num_inference_steps: values.numInferenceSteps,
        }),
      });

      if (!response.ok) {
        setStatusLabel("Failed to enqueue job");
        return;
      }

      const payload = (await response.json()) as { job_id: string };
      const jobId = payload.job_id;

      const source = new EventSource(`${apiBaseUrl}/api/status/${jobId}`);
      source.onmessage = (event: MessageEvent<string>) => {
        const data = JSON.parse(event.data) as {
          step: number;
          total: number;
          status: string;
          image_urls?: string[];
        };
        setCurrentStep(data.step);
        setTotalSteps(data.total);
        setStatusLabel(data.status);

        if (data.status === "completed" && data.image_urls?.length) {
          source.close();
          setImages(
            data.image_urls.map((src, index) => ({
              src: src.startsWith("http") ? src : `${apiBaseUrl}${src}`,
              alt: `Generated still ${index + 1}`,
            })),
          );
        }

        if (data.status === "failed") {
          source.close();
        }
      };

      source.onerror = () => {
        source.close();
      };
    })();
  }, []);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-zinc-50">StockFlow</h1>
        <p className="text-sm text-zinc-400">
          Local SDXL base pass, metadata, and Adobe Stock CSV export
        </p>
      </header>
      <GenerationForm
        onSubmit={handleSubmit}
        defaultWidth={512}
        defaultHeight={512}
        defaultSteps={20}
      />
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
        <ProgressBar
          currentStep={currentStep}
          totalSteps={totalSteps}
          label={statusLabel}
        />
      </div>
      {images.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-zinc-100">Outputs</h2>
          <ImageGallery images={images} />
        </section>
      ) : null}
    </main>
  );
}
