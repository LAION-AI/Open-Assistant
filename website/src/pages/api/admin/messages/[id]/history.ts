import { withAnyRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

export default withAnyRole(["moderator", "admin"], async (req, res, token) => {
  const { id } = req.query;

  const user = await getBackendUserCore(token.sub);
  const client = createApiClientFromUser(user);

  const revision_history = await client.fetch_message_revision_history(id as string);
  res.status(200).json(revision_history);
});
