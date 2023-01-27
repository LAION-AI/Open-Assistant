import { withoutRole } from "src/lib/auth";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const { id } = req.query;

  const user = await getBackendUserCore(token.sub);
  const params = new URLSearchParams({
    username: user.id,
    auth_method: user.auth_method,
  });

  const messageRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages/${id}/?${params}`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
  });
  const message = await messageRes.json();

  // Send recieved messages to the client.
  res.status(200).json(message);
});

export default handler;
