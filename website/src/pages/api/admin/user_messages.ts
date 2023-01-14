import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withRole("admin", async (req, res) => {
  const { user } = req.query;
  const messages = await oasstApiClient.fetch_user_messages(user);
  res.status(200).json(messages);
});

export default handler;
