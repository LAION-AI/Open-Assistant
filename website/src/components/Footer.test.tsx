import { render } from "@testing-library/react";
import { Footer } from "./Footer";

describe("Footer", () => {
  it("should render the footer component", () => {
    const { getByLabelText, getByText } = render(<Footer />);

    expect(getByLabelText("Home")).toBeInTheDocument();

    // Verify that the component displays the correct text content
    expect(getByText("Open Assistant")).toBeInTheDocument();
    expect(getByText("Conversational AI for everyone.")).toBeInTheDocument();

    // Verify that the legal and connect links are displayed and have the correct href attributes
    expect(getByText("Privacy Policy")).toHaveAttribute("href", "/privacy-policy");
    expect(getByText("Terms of Service")).toHaveAttribute("href", "/terms-of-service");
    expect(getByText("Github")).toHaveAttribute("href", "https://github.com/LAION-AI/Open-Assistant");
    expect(getByText("Discord")).toHaveAttribute("href", "https://ykilcher.com/open-assistant-discord");
  });
});
