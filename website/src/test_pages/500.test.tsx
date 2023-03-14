import { render, screen } from "@testing-library/react";
import ServerError from "../pages/500";

describe("ServerError", () => {
  it("renders server error message", () => {
    render(<ServerError />);
    const errorMessage = screen.getByText(/sorry, we encountered a server error/i);
    expect(errorMessage).toBeInTheDocument();
  });

  it("renders bug report link", () => {
    render(<ServerError />);
    const linkElement = screen.getByRole("link", { name: /report a bug/i });
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveAttribute("href", "https://github.com/LAION-AI/Open-Assistant/issues/new/choose");
    expect(linkElement).toHaveAttribute("target", "_blank");
    expect(linkElement).toHaveAttribute("rel", "noopener noreferrer");
  });
});
