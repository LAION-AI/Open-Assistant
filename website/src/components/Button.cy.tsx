import React from "react";
import { Button } from "./Button";

describe("<Button />", () => {
  it("renders", () => {
    // see: https://on.cypress.io/mounting-react
    cy.mount(<Button className="border-gray-800 m-5">Test button</Button>);
    cy.get("button").compareSnapshot("button-element");
  });
});
