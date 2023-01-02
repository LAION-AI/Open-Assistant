import { faker } from "@faker-js/faker";

describe("signin flow", () => {
  it("redirects to a confirmation page on submit of valid email address", () => {
    cy.visit("/auth/signin");
    cy.get('[data-cy="email-address"]').type(`test@example.com`);
    cy.get('[data-cy="signin-email-button"]').click();
    cy.url().should("contain", "/auth/verify");
  });
  it("emails a login link to the user when signing in with email", () => {
    // Use random email to avoid possibility of tests passing just due to other tests or previous runs also causing emails to be sent
    const emailAddress = faker.internet.email();
    cy.log("emailAddress", emailAddress);
    cy.request("GET", "/api/auth/csrf")
      .then((response) => {
        const csrfToken = response.body.csrfToken;
        cy.request("POST", "/api/auth/signin/email", {
          callbackUrl: "/",
          email: emailAddress,
          csrfToken,
          json: "true",
        });
      })
      .then((response) => {
        cy.signInUsingEmailedLink(emailAddress).then(() => {
          cy.get('[data-cy="username"]').should("exist");
        });
      });
  });
  it("shows the logged in users email address if logged in with email", () => {
    const emailAddress = "user@example.com";
    cy.signInWithEmail(emailAddress);
    // The user will only see the email address if the window is wide enough, not technically required as even when hidden this will find it in the page.
    cy.viewport(1920, 1000);
    cy.contains('[data-cy="username"]', emailAddress);
  });
});

export {};
