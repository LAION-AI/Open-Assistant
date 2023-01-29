describe("labeling assistant replies", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/label/label_assistant_reply");

    cy.get('[data-cy="task"]')
      .invoke("attr", "data-task-type")
      .then((type) => {
        cy.log("Task type", type);

        // For specific task pages the no task available result is normal.
        if (type === undefined) return;

        cy.get('[data-cy="label-question"]').each((label) => {
          // Click the no button, this generally approves the spam check
          cy.wrap(label).find('[data-cy="no"]').click();
        });
        cy.get('[data-cy="label-options"]').each((label) => {
          // Click the 4th option
          cy.wrap(label).find('[data-cy="radio-option"]').eq(3).click();
        });

        cy.get('[data-cy="review"]').click();

        cy.get('[data-cy="submit"]').click();
      });
  });
});

export {};
