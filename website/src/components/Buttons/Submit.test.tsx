import { render } from "@testing-library/react";
import { SubmitButton } from "./Submit";

describe("SubmitButton", () => {
  it("renders the button with the correct text", () => {
    // Render the component with the "Submit" text.
    const { getByText } = render(<SubmitButton>Submit</SubmitButton>);

    // Find the rendered button by its text content.
    const buttonElement = getByText("Submit");

    // Check that the button exists and has the correct text content.
    expect(buttonElement).toBeInTheDocument();
  });

  it("passes additional props to the button", () => {
    // Render the component with additional props.
    const { getByRole } = render(<SubmitButton data-testid="test-button">Submit</SubmitButton>);

    // Find the rendered button by its role and data-testid.
    const buttonElement = getByRole("button", { name: "Submit" });
    const testIdAttribute = buttonElement.getAttribute("data-testid");

    // Check that the button exists and has the correct attributes.
    expect(buttonElement).toBeInTheDocument();
    expect(testIdAttribute).toBe("test-button");
  });
});
