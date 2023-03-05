/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

Cypress.Commands.add("signInUsingEmailedLink", (emailAddress) => {
  const mailDevApi = `${Cypress.env("MAILDEV_PROTOCOL")}://${Cypress.env("MAILDEV_HOST")}:${Cypress.env(
    "MAILDEV_API_PORT"
  )}`;
  cy.request("GET", `${mailDevApi}/email?headers.to=${emailAddress.toLowerCase()}`).then((response) => {
    const emails = response.body;

    // Find and use login link
    const loginLink = emails.pop().html.match(/href="[^"]+(\/api\/auth\/callback\/[^"]+?)"/)[1];
    cy.visit(loginLink);
    cy.url().should("include", "/dashboard");

    // we do a GET to this url to force the python backend to add an entry for our user
    // in the database, otherwise the tos acceptance will error with 404 user not found
    // then we accept the tos
    cy.request("GET", "/api/available_tasks?lang=en").then(() => cy.request("POST", "/api/tos", {}));
  });
});

Cypress.Commands.add("signInWithEmail", (emailAddress) => {
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
    .then(() => {
      cy.signInUsingEmailedLink(emailAddress);
    });
});

export {};
