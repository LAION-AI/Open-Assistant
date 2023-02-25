import { render, screen } from "@testing-library/react";
import Home from "src/pages/index";

describe("Home page", () => {
  it("should render correctly", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Open Assistant");
  });
});
