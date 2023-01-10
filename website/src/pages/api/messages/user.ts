import { withoutRole } from "src/lib/auth";

const handler = withoutRole("banned", async (req, res, token) => {
  //TODO: add params if needed
  const params = new URLSearchParams({
    username: token.sub,
  });

  const messagesRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages?${params}`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });
  const messages = await messagesRes.json();

  // Send recieved messages to the client.
  res.status(200).json(messages);
});

export default handler;
