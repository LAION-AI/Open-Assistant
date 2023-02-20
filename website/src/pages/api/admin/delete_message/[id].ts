import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const { id } = req.query;
  try {
    const client = await createApiClient(token);
    await client.delete_message(id as string);
    res.status(200).json({ message: "Message deleted" });
  } catch (e) {
    res.status(500).json({ message: "Failed to delete message" });
  }
});

export default handler;
