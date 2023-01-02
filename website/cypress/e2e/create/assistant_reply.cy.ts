import { faker } from "@faker-js/faker";

describe("replying as the assistant", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/create/assistant_reply");

    cy.get('[data-cy="task-id"').then((taskIdElement) => {
      const taskId = taskIdElement.text();

      const reply = faker.lorem.sentence();
      cy.log("reply", reply);
      cy.get('[data-cy="reply"').type(reply);

      cy.get('[data-cy="submit"]').click();

      cy.get('[data-cy="next-task"]').click();

      cy.get('[data-cy="task-id"').should((taskIdElement) => {
        expect(taskIdElement.text()).not.to.eq(taskId);
      });
    });
  });
});

export {};
