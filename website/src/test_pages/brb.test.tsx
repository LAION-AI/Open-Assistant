import { render, screen } from "@testing-library/react";
import BrbPage from "../pages/brb";

describe("BrbPage", () => {
  it("renders the maintenance message", () => {
    render(<BrbPage />);
    const maintenanceMessage = screen.getByText(/We are improving the service/i);
    expect(maintenanceMessage).toBeInTheDocument();
  });
});
