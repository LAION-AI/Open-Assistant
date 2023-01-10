import { fireEvent, render, screen } from "@testing-library/react";
import { RouterContext } from "next/dist/shared/lib/router-context";
import React from "react";
import { createMockRouter } from "src/test-utils/createMockRouter";

import { OptionProps, TaskOption } from "./TaskOption";

describe("TaskOption component", () => {
  const testProps: OptionProps = {
    title: "Task Title",
    alt: "Task Title",
    img: "/imgPath",
    link: "/fake/path",
  };

  it("should render", () => {
    render(<TaskOption {...testProps} />);
    expect(screen.getByRole("heading")).toHaveTextContent("Task Title");
    expect(screen.getByRole("img")).toHaveAttribute("alt", "Task Title");
    expect(screen.getByRole("link")).toHaveAttribute("href", "/fake/path");
  });

  it("should navigate properly on click", () => {
    const router = createMockRouter({ pathname: "/fake/path" });
    render(
      <RouterContext.Provider value={router}>
        <TaskOption {...testProps} />
      </RouterContext.Provider>
    );
    expect(screen.getByRole("link")).toHaveAttribute("href", "/fake/path");
    fireEvent.click(screen.getByRole("link"));
    expect(router.push).toHaveBeenCalledWith("/fake/path", expect.anything(), expect.anything());
  });
});
