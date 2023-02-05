import { withRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withRole("admin", async (req, res, token) => {
  const { id } = req.query;
  try {
    const client = await createApiClient(token);
    await client.stop_tree(id as string);
    res.status(200).json({ message: `Tree ${id} stopped`, id });
  } catch (e) {
    res.status(500).json(e);
  }
});

export default handler;
