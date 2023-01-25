import { OasstApiClient, OasstError } from "src/lib/oasst_api_client";
import type { BackendUserCore } from "src/types/Users";

describe("Contract test for Oasst API", function () {
  // Assumes this is running the mock server.
  const oasstApiClient = new OasstApiClient("http://localhost:8080", "test");

  const testUser = {
    id: "abcd",
    display_name: "test",
    auth_method: "local",
  } as BackendUserCore;

  it("can fetch a task", async () => {
    expect(await oasstApiClient.fetchTask("random", testUser, "en")).to.be.not.null;
  });

  it("can ack a task", async () => {
    const task = await oasstApiClient.fetchTask("random", testUser, "en");
    expect(await oasstApiClient.ackTask(task.id, "321")).to.be.null;
  });

  it("can record a taskInteraction", async () => {
    const task = await oasstApiClient.fetchTask("random", testUser, "en");
    expect(
      await oasstApiClient.interactTask("text_reply_to_message", task.id, "321", "1", { text: "Test" }, testUser, "en")
    ).to.be.not.null;
  });

  // Note: Below here are unittests for OasstApiClient, not contract tests. They still fit here because
  // the other contract tests are also testing the OasstApiClient.
  const callApiMethod = () => {
    return oasstApiClient.ackTask("", "");
  };

  it("should return null for a 204 response", async () => {
    const mockFetch = cy.stub(global, "fetch").resolves({
      status: 204,
    });

    const result = await callApiMethod();
    assert.isNull(result);

    mockFetch.restore();
  });

  it("should throw an OasstError with data from the response for a non-2XX response with a valid OasstError response", async () => {
    const mockFetch = cy.stub(global, "fetch").resolves({
      status: 400,
      text: () =>
        // Note: this is vulnerable to interface changes in the Oasst API.
        // The python tests use a Pydantic model to ensure this object is always valid,
        // but we don't have that here.
        // This could be a case for generating Zod schemas from OpenAPI.
        Promise.resolve(
          JSON.stringify({
            message: "error message",
            error_code: 1000,
          })
        ),
    });

    try {
      await callApiMethod();
      assert.fail();
    } catch (error) {
      assert.instanceOf(error, OasstError);
      if (error instanceof OasstError) {
        assert.equal(error.errorCode, 1000);
        assert.equal(error.message, "error message");
        assert.equal(error.httpStatusCode, 400);
      }
    }

    mockFetch.restore();
  });

  it("should throw a generic OasstError with the text from the response for a non-2XX response with an unknown format", async () => {
    const mockFetch = cy.stub(global, "fetch").resolves({
      status: 400,
      text: () => Promise.resolve("error message"),
    });

    try {
      await callApiMethod();
      assert.fail();
    } catch (error) {
      assert.instanceOf(error, OasstError);
      assert.equal(error.message, "error message");
    }

    mockFetch.restore();
  });
});
