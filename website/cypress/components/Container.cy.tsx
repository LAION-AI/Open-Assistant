import React from "react";
import { Container } from "src/components/Container";

describe("<Container />", () => {
  it("renders", () => {
    // see: https://on.cypress.io/mounting-react
    const className = "my-class";
    const text = "test_container";
    cy.mount(<Container className={className}>{text}</Container>);
    cy.get(`div.${className}`)
      .should("have.class", className)
      .should("be.visible")
      .should("contain", text);
  });
});
