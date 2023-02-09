import { withRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withRole("admin", async (req, res, token) => {
  const { user } = req.query;
  console.log(user);
  const oasstApiClient = await createApiClient(token);
  const messages = await oasstApiClient.fetch_user_messages(user as string);
  res.status(200).json(messages);
});

export default handler;
