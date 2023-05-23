import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

export default withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const messageId = req.query.id as string;
  // const isModOrAdmin = token.role === ROLES.ADMIN || token.role === ROLES.MODERATOR;
  const edits = await client.fetch_message_edits(messageId);

  if (!edits) {
    return res.json(edits);
  }

  return res.json(edits);
});
