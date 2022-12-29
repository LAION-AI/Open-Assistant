import React from "react";
import { Button } from "./Button";

describe("<Button />", () => {
  it("renders", () => {
    // see: https://on.cypress.io/mounting-react
    cy.mount(<Button className="border-gray-300">Test button</Button>);
  });
});
