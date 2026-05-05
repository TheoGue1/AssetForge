import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { GenerationForm, type GenerationFormValues } from "../GenerationForm";

describe("GenerationForm", () => {
  it("renders prompt, subject, background, and batch size fields", () => {
    render(<GenerationForm onSubmit={vi.fn()} />);
    expect(screen.getByLabelText(/prompt/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/subject/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/background/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/batch size/i)).toBeInTheDocument();
  });

  it("submits parsed values to the handler", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<GenerationForm onSubmit={onSubmit} defaultWidth={512} defaultHeight={512} defaultSteps={20} />);

    await user.type(screen.getByLabelText(/prompt/i), "soft light");
    await user.type(screen.getByLabelText(/subject/i), "strawberry");
    await user.type(screen.getByLabelText(/background/i), "white");
    const batchInput = screen.getByLabelText(/batch size/i);
    fireEvent.change(batchInput, { target: { value: "2" } });
    await user.click(screen.getByRole("button", { name: /generate/i }));

    const expected: GenerationFormValues = {
      prompt: "soft light",
      subject: "strawberry",
      background: "white",
      batchSize: 2,
      width: 512,
      height: 512,
      numInferenceSteps: 20,
    };
    expect(onSubmit).toHaveBeenCalledWith(expected);
  });
});
