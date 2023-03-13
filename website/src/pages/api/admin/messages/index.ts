import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const messages = await client.fetch_messages_cursor({
    direction: req.query.direction as "back",
    cursor: req.query.cursor as string,
    desc: true,
    include_deleted: true,
    lang: req.query.lang as string,
    max_count: 10,
    user_id: req.query.user_id as string,
    include_user: !!req.query.include_user,
  });
  res.status(200).json(messages);
});

export default handler;
