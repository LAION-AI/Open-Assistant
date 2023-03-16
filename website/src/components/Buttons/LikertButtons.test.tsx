import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LikertButtons } from "./LikertButtons";

describe("LikertButtons", () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  test("should call onChange function with correct value", () => {
    const count = 5;
    render(<LikertButtons isDisabled={false} count={count} onChange={mockOnChange} />);
    const option = screen.getByLabelText("0");
    userEvent.click(option);
    expect(mockOnChange).toHaveBeenCalledWith(0);
  });

  test("should render correct number of options", () => {
    const count = 7;
    render(<LikertButtons isDisabled={false} count={count} onChange={mockOnChange} />);
    const options = screen.getAllByRole("radio");
    expect(options).toHaveLength(count);
  });

  test("should render disabled when isDisabled is true", () => {
    const count = 3;
    render(<LikertButtons isDisabled={true} count={count} onChange={mockOnChange} />);
    const options = screen.getAllByRole("radio");
    expect(options[0]).toBeDisabled();
  });
});
