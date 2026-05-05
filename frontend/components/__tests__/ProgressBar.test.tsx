import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProgressBar } from "../ProgressBar";

describe("ProgressBar", () => {
  it("reflects percentage from current and total steps", () => {
    render(<ProgressBar currentStep={10} totalSteps={40} label="Rendering" />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "25");
    expect(screen.getByText("25%")).toBeInTheDocument();
  });
});
