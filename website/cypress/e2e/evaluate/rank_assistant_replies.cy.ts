describe("ranking prompter replies", () => {
  it("completes the current task on submit and on request shows a new task", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.visit("/evaluate/rank_user_replies");

    cy.get('[data-cy="task-id"').then((taskIdElement) => {
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

      cy.get('[data-cy="next-task"]').click();

      cy.get('[data-cy="task-id"').should((taskIdElement) => {
        expect(taskIdElement.text()).not.to.eq(taskId);
      });
    });
  });
});

export {};
