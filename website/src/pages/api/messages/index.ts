import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const messages = await client.fetch_recent_messages();
  res.status(200).json(messages);
});

export default handler;
