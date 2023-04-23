import { render } from "@testing-library/react";
import { AnimatedCircles } from "./AnimatedCircles";

describe("AnimatedCircles", () => {
  it("should render the AnimatedCircles component", () => {
    const { container } = render(<AnimatedCircles />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should apply the correct classes and styles", () => {
    const { container } = render(<AnimatedCircles />);
    const svgElements = container.querySelectorAll("svg");

    expect(container.firstChild).toHaveClass("absolute");
    expect(svgElements).toHaveLength(2);

    svgElements.forEach((svg) => {
      expect(svg).toHaveClass("absolute", "inset-0", "h-full", "w-full");
    });
  });
});
