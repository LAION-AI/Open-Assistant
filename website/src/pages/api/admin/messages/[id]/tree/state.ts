import { withRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

export default withRole("admin", async (req, res, token) => {
  const client = await createApiClient(token);
  const messageId = req.query.id as string;
  const treeState = await client.fetch_message_tree_state(messageId);


  return res.json(treeState);
});


