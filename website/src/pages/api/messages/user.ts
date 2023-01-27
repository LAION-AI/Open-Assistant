import { withoutRole } from "src/lib/auth";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const params = new URLSearchParams({
    username: user.id,
    auth_method: user.auth_method,
  });

  // TODO: move to oasst_api_client

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
