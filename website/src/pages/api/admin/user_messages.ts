import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import type { Message } from "src/types/Conversation";

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withRole("admin", async (req, res) => {
  const { user } = req.query;
  const messages: Message[] = await oasstApiClient.fetch_user_messages(user as string);
  res.status(200).json(messages);
});

export default handler;
