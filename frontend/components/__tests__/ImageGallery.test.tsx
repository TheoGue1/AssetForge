import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ImageGallery } from "../ImageGallery";

describe("ImageGallery", () => {
  it("renders a grid of provided images", () => {
    const images = [
      { src: "/a.png", alt: "first" },
      { src: "/b.png", alt: "second" },
    ];
    render(<ImageGallery images={images} />);
    expect(screen.getByAltText("first")).toHaveAttribute("src", "/a.png");
    expect(screen.getByAltText("second")).toHaveAttribute("src", "/b.png");
  });
});
