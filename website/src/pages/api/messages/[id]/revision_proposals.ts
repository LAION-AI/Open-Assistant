import { withoutRole } from "src/lib/auth";
import { OasstApiClient } from "src/lib/oasst_api_client";
import { createApiClient } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

export default withoutRole("banned", async (req, res, token) => {
  const client: OasstApiClient = await createApiClient(token);
  const messageId = req.query.id as string;
  const user = await getBackendUserCore(token.sub);
  // const isModOrAdmin = token.role === ROLES.ADMIN || token.role === ROLES.MODERATOR;
  const proposals = await client.fetch_message_revision_proposals(messageId);
  const message = await client.fetch_message(messageId, user);

  return res.json({
    ...proposals,
    message
  });
});
