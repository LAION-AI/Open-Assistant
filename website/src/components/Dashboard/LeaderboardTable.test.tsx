import { render, screen } from "@testing-library/react";
import { LeaderboardTable } from "./LeaderboardTable";

describe("LeaderboardTable", () => {
  it("renders the correct title and link", () => {
    render(<LeaderboardTable />);
    const title = screen.getByText(/Top 5 Contributors Today/i);
    const link = screen.getByText(/View All/i).closest("a");
    expect(title).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/leaderboard");
  });
});
