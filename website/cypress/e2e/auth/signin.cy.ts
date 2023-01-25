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
        cy.request({
          method: "POST",
          url: "/api/auth/signin/email",
          body: {
            callbackUrl: "/",
            email: emailAddress,
            csrfToken,
            json: "true",
            captcha: "XXXX.DUMMY.TOKEN.XXXX",
          },
        });
      })
      .then((response) => {
        cy.signInUsingEmailedLink(emailAddress).then(() => {
          cy.get('[data-cy="username"]').should("exist");
        });
      });
  });
});

export {};
