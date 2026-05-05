import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProgressBar } from "../ProgressBar";

describe("vitest + RTL", () => {
  it("mounts a component", () => {
    render(<ProgressBar currentStep={1} totalSteps={4} />);
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });
});
