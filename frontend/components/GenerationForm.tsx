"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export type GenerationFormValues = {
  prompt: string;
  subject: string;
  background: string;
  batchSize: number;
  width: number;
  height: number;
  numInferenceSteps: number;
};

export function GenerationForm({
  onSubmit,
  defaultWidth = 512,
  defaultHeight = 512,
  defaultSteps = 25,
}: {
  onSubmit: (values: GenerationFormValues) => void;
  defaultWidth?: number;
  defaultHeight?: number;
  defaultSteps?: number;
}) {
  const [prompt, setPrompt] = useState("");
  const [subject, setSubject] = useState("");
  const [background, setBackground] = useState("");
  const [batchSize, setBatchSize] = useState(1);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit({
      prompt,
      subject,
      background,
      batchSize,
      width: defaultWidth,
      height: defaultHeight,
      numInferenceSteps: defaultSteps,
    });
  }

  return (
    <Card className="border-zinc-800 bg-zinc-950">
      <CardHeader>
        <CardTitle className="text-zinc-50">Generation brief</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <div className="grid gap-2">
            <Label htmlFor="prompt">Prompt</Label>
            <Input
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Lighting and mood notes"
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              name="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Primary subject"
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="background">Background</Label>
            <Input
              id="background"
              name="background"
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="e.g., pure white sweep"
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="batchSize">Batch size</Label>
            <Input
              id="batchSize"
              name="batchSize"
              type="number"
              min={1}
              max={16}
              value={batchSize}
              onChange={(e) => setBatchSize(Number.parseInt(e.target.value || "1", 10))}
              required
            />
          </div>
          <Button type="submit" variant="secondary">
            Generate
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
