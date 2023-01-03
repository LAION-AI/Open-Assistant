import { faker } from "@faker-js/faker";

describe("creating initial prompts", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/create/initial_prompt");

    cy.get('[data-cy="task-id"').then((taskIdElement) => {
      const taskId = taskIdElement.text();

      const prompt = faker.lorem.sentence();
      cy.log("prompt", prompt);
      cy.get('[data-cy="reply"').type(prompt);

      cy.get('[data-cy="submit"]').click();

      cy.get('[data-cy="next-task"]').click();

      cy.get('[data-cy="task-id"').should((taskIdElement) => {
        expect(taskIdElement.text()).not.to.eq(taskId);
      });
    });
  });
});

export {};
