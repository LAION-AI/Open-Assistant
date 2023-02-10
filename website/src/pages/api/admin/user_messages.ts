import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const LIMIT = 10;

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const { cursor, direction, user } = req.query;

  const oasstApiClient = await createApiClient(token);

  const response = await oasstApiClient.fetch_user_messages_cursor(user as string, {
    include_deleted: true,
    direction: direction as "back",
    cursor: cursor as string,
    max_count: LIMIT,
    desc: true,
  });

  res.status(200).json(response);
});

export default handler;
