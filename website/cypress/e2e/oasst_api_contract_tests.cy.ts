import OasstApiClient from "src/lib/oasst_api_client";

describe("Contract test for Oasst API", function () {
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
});
