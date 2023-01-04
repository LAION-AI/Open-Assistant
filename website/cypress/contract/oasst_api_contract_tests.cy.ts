import OasstApiClient from "src/lib/oasst_api_client";

describe("Contract test for Oasst API", function () {
  // Assumes this is running the mock server.
  const oasstApiClient = new OasstApiClient("http://localhost:8080", "test");

  it("can fetch a task", async () => {
    expect(
      await oasstApiClient.fetchTask("random", {
        sub: "test",
        name: "test",
        email: "test",
      })
    ).to.be.not.null;
  });

  it("can ack a task", async () => {
    const task = await oasstApiClient.fetchTask("random", {
      sub: "test",
      name: "test",
      email: "test",
    });
    expect(await oasstApiClient.ackTask(task.id, "321")).to.be.null;
  });

  // TODO(#354): Add test for 204
  // TODO(#354): Add test for parsing >=300, throwing an OasstError
  // TODO(#354): Add test for parsing >=300, throwing a generic error
});
