import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const { id } = req.query;
  const user = await getBackendUserCore(token.sub);
  const client = createApiClientFromUser(user);
  const message = await client.fetch_message(id as string, user);
  res.status(200).json(message);
});

export default handler;
