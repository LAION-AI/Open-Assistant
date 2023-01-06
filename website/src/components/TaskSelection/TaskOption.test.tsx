import { render, screen } from "@testing-library/react";
import React from "react";

import { OptionProps, TaskOption } from "./TaskOption";

describe("TaskOption component", () => {
  const testProps: OptionProps = {
    alt: "Task Title",
    img: "/imgPath",
    title: "Task Title",
    link: "/create/summarize_story",
  };

  beforeEach(() => {
    render(<TaskOption {...testProps} />);
  });

  it("should render Task Option component", () => {
    expect(screen.getByRole("heading")).toHaveTextContent(testProps.title);
    expect(screen.getByRole("link")).toHaveAttribute("href", testProps.link);
    expect(screen.queryByText("hi")).toBeNull();
  });
});
