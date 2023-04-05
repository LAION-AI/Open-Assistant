import { ROLES } from "src/components/RoleSelect";
import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  let userid: string;
  const isModOrAdmin = token.role === ROLES.ADMIN || token.role === ROLES.MODERATOR;

  // uid query param is only allowed for moderators and admins else it will be ignored and the user's own stats will be returned
  if (req.query.uid && isModOrAdmin) {
    // uid is web user's id
    userid = typeof req.query.uid === "string" ? req.query.uid : req.query.uid[0];
  } else {
    userid = token.sub;
  }

  const user = await getBackendUserCore(userid as string);
  const oasstApiClient = createApiClientFromUser(user);
  const stats = await oasstApiClient.fetch_user_stats(user);
  res.status(200).json(stats);
});

export default handler;
