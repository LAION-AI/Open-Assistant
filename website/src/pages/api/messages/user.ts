import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const LIMIT = 10;

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const client = createApiClientFromUser(user);
  const { cursor, direction } = req.query;

  const messages = await client.fetch_my_messages_cursor(user, {
    direction: direction as "back",
    cursor: cursor as string,
    max_count: LIMIT,
    desc: true,
  });

  res.status(200).json(messages);
});

export default handler;
