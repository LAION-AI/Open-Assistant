// load type definitions that come with Cypress module
/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to sign in with a given email address
       * @example cy.signInWithEmail('user@example.com')
       */
      signInWithEmail(emailAddress: string): Chainable<Element>;

      /**
       * Custom command to sign in with the link emailed to the given email address
       * @example cy.signInUsingEmailedLink('user@example.com')
       */
      signInUsingEmailedLink(emailAddress: string): Chainable<Element>;
    }
  }
}

export {};
