describe("empty spec", () => {
  it("passes", () => {
    cy.visit("/auth/signin");
    cy.get(".chakra-input").type(`test@example.com`);
    cy.get(".chakra-stack > .chakra-button").click();
    cy.url().should("contain", "/auth/verify");
  });
});

export {};
