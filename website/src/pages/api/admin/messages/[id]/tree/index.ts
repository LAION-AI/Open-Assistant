import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { buildTree } from "src/utils/buildTree";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const client = await createApiClient(token);
  const messageId = req.query.id as string;
  const response = await client.fetch_message_tree(messageId, {
    include_deleted: true,
    include_spam: true,
  });
  const treeState = await client.fetch_message_tree_state(messageId);

  if (!response) {
    return res.json({ tree: null });
  }

  const tree = buildTree(response.messages);

  return res.json({ tree, message: response.messages.find((m) => m.id === messageId), tree_state: treeState });
});
