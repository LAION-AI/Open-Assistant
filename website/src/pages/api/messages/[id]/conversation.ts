import { withoutRole } from "src/lib/auth";

const handler = withoutRole("banned", async (req, res) => {
  const { id } = req.query;

  const messagesRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages/${id}/conversation`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
  });
  const messages = await messagesRes.json();

  // Send recieved messages to the client.
  res.status(200).json(messages);
});

export default handler;
