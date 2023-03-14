import { render, fireEvent } from "@testing-library/react";
import { SkipButton } from "./Skip";

describe("SkipButton", () => {
  it("calls onSkip with input value when Send button is clicked", () => {
    const onSkip = jest.fn();
    const { getByText, getByPlaceholderText } = render(<SkipButton onSkip={onSkip} />);

    fireEvent.click(getByText("Skip"));

    const input = getByPlaceholderText("Any feedback on this task?");
    fireEvent.change(input, { target: { value: "I want to skip this task." } });

    fireEvent.click(getByText("Send"));

    expect(onSkip).toHaveBeenCalledTimes(1);
    expect(onSkip).toHaveBeenCalledWith("I want to skip this task.");
  });
});
