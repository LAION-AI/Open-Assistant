import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    // No baseUrl here, because we don't need it for contract testing
    baseUrl: null,
    specPattern: "cypress/contract/*.cy.{ts,js}",
  },
});
