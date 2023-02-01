import { withRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import type { Message } from "src/types/Conversation";

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withRole("admin", async (req, res, token) => {
  const { user } = req.query;
  const oasstApiClient = await createApiClient(token);
  const messages: Message[] = await oasstApiClient.fetch_user_messages(user as string);
  res.status(200).json(messages);
});

export default handler;
