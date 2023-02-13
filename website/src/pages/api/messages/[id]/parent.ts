import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const { id } = req.query;

  if (!id) {
    res.status(400).end();
    return;
  }

  const user = await getBackendUserCore(token.sub);
  const client = createApiClientFromUser(user);
  const message = await client.fetch_message(id as string, user);

  if (!message.parent_id) {
    res.status(404).end();
    return;
  }

  const parent = await client.fetch_message(message.parent_id, user);
  res.status(200).json(parent);
});

export default handler;
