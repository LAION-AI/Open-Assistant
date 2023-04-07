import { ROLES } from "src/components/RoleSelect";
import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { buildTree } from "src/pages/api/admin/messages/[id]/tree";

export default withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const messageId = req.query.id as string;
  const isModOrAdmin = token.role === ROLES.ADMIN || token.role === ROLES.MODERATOR;
  const response = await client.fetch_message_tree(messageId, {
    include_deleted: isModOrAdmin,
    include_spam: true,
  });

  if (!response) {
    return res.json({ tree: null });
  }

  const tree = buildTree(response.messages);

  return res.json({ tree, message: response.messages.find((m) => m.id === messageId) });
});
