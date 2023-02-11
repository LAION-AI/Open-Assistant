import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { getUserLanguage } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const userLanguage = getUserLanguage(req);
  const messages = await client.fetch_recent_messages(userLanguage);
  res.status(200).json(messages);
});

export default handler;
