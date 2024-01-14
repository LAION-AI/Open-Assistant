import { render, screen } from "@testing-library/react";
import Home from "src/pages/index";
import { TestProviders } from "src/test-utils/TestProviders";

describe("Home page", () => {
  it("should render correctly", () => {
    render(
      <TestProviders>
        <Home />
      </TestProviders>
    );
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Open Assistant");
  });
});
