import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const { id } = req.query;
  const halt = req.body as boolean;
  try {
    const client = await createApiClient(token);
    await client.set_tree_halted(id as string, req.body as boolean);
    res.status(200).json({ message: `Tree ${id} restarted`, id, halted: halt });
  } catch (e) {
    res.status(500).json(e);
  }
});

export default handler;
