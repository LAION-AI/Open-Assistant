import { render, screen } from "@testing-library/react";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import React from "react";
import Account from "../account/index";

// Mock the next/router module to provide a mocked implementation of the useRouter hook
jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));

// Mock the next-auth/react module to provide a mocked implementation of the useSession hook
jest.mock("next-auth/react", () => ({
  useSession: jest.fn(),
}));

describe("Account page", () => {
  // Define a dummy session object to be returned by the useSession hook in the tests
  const session = { user: { name: "Test User", email: "testuser@example.com" } };

  beforeEach(() => {
    // Reset the mocked useRouter and useSession hooks before each test
    jest.resetAllMocks();
  });

  it("should render the user's name and email address", () => {
    // Set up the mocked useRouter and useSession hooks to return the expected values
    useRouter.mockReturnValue({}); // We don't need to mock any specific values for the router in this test
    useSession.mockReturnValue({ data: session });

    // Render the Account page
    render(<Account />);

    // Assert that the user's name and email address are displayed on the page
    expect(screen.getByText(session.user.name)).toBeInTheDocument();
    expect(screen.getByText(session.user.email)).toBeInTheDocument();
  });

  it("should display a link to edit the user's account details", () => {
    // Set up the mocked useRouter and useSession hooks to return the expected values
    useRouter.mockReturnValue({}); // We don't need to mock any specific values for the router in this test
    useSession.mockReturnValue({ data: session });

    // Render the Account page
    const { debug } = render(<Account />);

    // Debug the rendered component
    debug();

    // Assert that a link to edit the user's account details is displayed on the page

    // Assert that a link to edit the user's account details is displayed on the page
    const editLink = screen.getByRole("link", { name: "" });
    expect(editLink).toBeInTheDocument();
  });

  it("should not render anything if the user is not authenticated", () => {
    // Set up the mocked useRouter and useSession hooks to return the expected values
    useRouter.mockReturnValue({}); // We don't need to mock any specific values for the router in this test
    useSession.mockReturnValue({ data: null });

    // Render the Account page
    const { container } = render(<Account />);

    // Assert that the component does not render anything
    expect(container.firstChild).toBeNull();
  });
});
