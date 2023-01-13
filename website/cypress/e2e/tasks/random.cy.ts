import { faker } from "@faker-js/faker";

describe("handles random tasks", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/tasks/random");

    // Check all create tasks.
    cy.get('[data-cy="task"]').then((createTaskElement) => {
      if (createTaskElement.find('[data-task-type="create-task"]').length) {
        cy.get('[data-cy="task-id"]').then((taskIdElement) => {
          const taskId = taskIdElement.text();

          const reply = faker.lorem.sentence();
          cy.log("reply", reply);
          cy.get('[data-cy="reply"]').type(reply);

          cy.get('[data-cy="submit"]').click();

          cy.get('[data-cy="task-id]"').should((taskIdElement) => {
            expect(taskIdElement.text()).not.to.eq(taskId);
          });
        });
      }

      // Check all Evaluate tasks.
      if (createTaskElement.find('[data-task-type="evaluate-task"]').length) {
        cy.get('[data-cy="task-id"]').then((taskIdElement) => {
          const taskId = taskIdElement.text();

          // Rank an item using the keyboard so that the submit button is enabled
          cy.get('button[aria-roledescription="sortable"]')
            .first()
            .click()
            .type("{enter}")
            .wait(100)
            .type("{downArrow}")
            .wait(100)
            .type("{enter}");

          cy.get('[data-cy="submit"]').click();

          cy.get('[data-cy="task-id"]').should((taskIdElement) => {
            expect(taskIdElement.text()).not.to.eq(taskId);
          });
        });
      }

      if (createTaskElement.find('[data-task-type="label-task"]').length) {
      }

      // TODO(#623): Figure out how to fail the test if none of the checks above pass.
    });
  });
});

export {};
