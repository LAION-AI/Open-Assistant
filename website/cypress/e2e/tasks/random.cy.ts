import { faker } from "@faker-js/faker";

describe("handles random tasks", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/tasks/random");

    // Do some tasks
    for (let taskNum = 0; taskNum < 10; taskNum++) {
      cy.get('[data-cy="task"]')
        .invoke("attr", "data-task-type")
        .then((type) => {
          cy.log("Task type", type);

          cy.get('[data-cy="task-id"]').then((taskIdElement) => {
            const taskId = taskIdElement.text();

            switch (type) {
              case "create-task": {
                const reply = faker.lorem.sentence();
                cy.log("reply", reply);
                cy.get('[data-cy="reply"]').type(reply);

                cy.get('[data-cy="review"]').click();

                cy.get('[data-cy="submit"]').click();
                break;
              }
              case "evaluate-task": {
                // Rank an item using the keyboard so that the submit button is enabled
                cy.get('[aria-roledescription="sortable"]')
                  .first()
                  .click()
                  .type("{enter}")
                  .wait(100)
                  .type("{downArrow}")
                  .wait(100)
                  .type("{enter}");

                cy.get('[data-cy="review"]').click();

                cy.get('[data-cy="submit"]').click();

                break;
              }
              case "label-task": {
                // Clicking on the slider will set the value to about the middle where it clicks
                cy.get('[aria-roledescription="slider"]').first().click();

                cy.get('[data-cy="review"]').click();

                cy.get('[data-cy="submit"]').click();

                break;
              }
              default:
                throw new Error(`Unexpected task type: ${type}`);
            }

            cy.get('[data-cy="task-id"]').should((taskIdElement) => {
              expect(taskIdElement.text()).not.to.eq(taskId);
            });
          });
        });
    }
  });
});

export {};
