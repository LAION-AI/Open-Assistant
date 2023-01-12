import { withRole } from "src/lib/auth";

const handler = withRole("admin", async (req, res, token) => {
  const { user } = req.query;

  const messagesRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/frontend_users/local/${user}/messages`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });
  const messages = await messagesRes.json();
  res.status(200).json(messages);
});

export default handler;
