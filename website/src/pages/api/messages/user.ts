import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const client = createApiClientFromUser(user);
  const messages = await client.fetch_my_messages(user);
  res.status(200).json(messages);
});

export default handler;
