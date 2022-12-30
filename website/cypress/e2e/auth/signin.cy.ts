describe("signin flow", () => {
  it("redirects to a confirmation page on submit of valid email address", () => {
    cy.visit("/auth/signin");
    cy.get(".chakra-input").type(`test@example.com`);
    cy.get(".chakra-stack > .chakra-button").click();
    cy.url().should("contain", "/auth/verify");
  });
});

export {};
