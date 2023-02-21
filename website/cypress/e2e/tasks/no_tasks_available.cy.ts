describe("no tasks available", () => {
  it("displays an empty state when no tasks are available", () => {
    cy.signInWithEmail("cypress@example.com");
    cy.intercept(
      {
        method: "GET",
        url: "/api/new_task/prompter_reply?lang=en",
      },
      {
        statusCode: 500,
        body: {
          message: "No tasks of type 'label_prompter_reply' are currently available.",
          errorCode: 1006,
          httpStatusCode: 503,
        },
      }
    ).as("newTaskPrompterReply");
    cy.visit("/create/user_reply");
    cy.wait("@newTaskPrompterReply").then(() => {
      cy.get('[data-cy="cy-no-tasks"]').should("exist");
    });
  });
});
