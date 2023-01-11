import { render, screen } from "@testing-library/react";
import AboutPage from "src/pages/about";

describe("About page", () => {
  it("should render correctly", () => {
    render(<AboutPage />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("What is OpenAssistant?");
  });
});
