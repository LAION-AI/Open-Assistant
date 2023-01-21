# Unit testing with Jest and React Testing Library

[Jest](https://jestjs.io/) is a test runner that is commonly coupled with
[React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) for creating unit tests.

## Creating tests

To begin writing tests, create a file ending in `.test.ts` for non-React code or a file ending with `.test.tsx` for
testing React code. For example, a test file for React component `TaskOption.tsx` would be named `TaskOption.test.tsx`
and would be created within the same directory as the component.

```
// TaskOption.test.tsx
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

```

This is a test that checks if the component has rendered correctly and if it navigates properly on click. The testing
methods, component, and its props type are imported. The `describe` is a Jest method that is used to group related tests
together while the `it` is what actually runs a test.

A testProps object is created and passed to the component to be rendered using the `render` method. Now it can be
tested. Query methods like `getByRole` and others listed in the
[testing library's docs](https://testing-library.com/docs/react-testing-library/cheatsheet#queries) can be used to
search for elements in the page. Finally, `expect` is run on those elements to see if they match the values in the props
that were originally declared. If they match, the test passes. If they do not match or if an error occurs, the test
fails.

In the second test, a mock router is used to simulate Next's router. The TaskOption component is rendered with the
router as its parent. To simulate a click, `fireEvent.click()` is used on the element with the role of "link". Finally,
the router can be tested by verifying that the `router.push` method was called with the correct path. Since the push
method is also called with two more arguments `as` and `options` that aren't useful for this specific test,
`expect.anything()` is used to ensure that those arguments are not null or undefined.

## Running tests

```
npm run jest
```
