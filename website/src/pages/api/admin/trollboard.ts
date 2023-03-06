import { withAnyRole } from "src/lib/auth";
import { updateUsersDisplayNames, updateUsersProfilePictures } from "src/lib/leaderboard_utilities";
import { createApiClient } from "src/lib/oasst_client_factory";
import { TrollboardTimeFrame } from "src/types/Trollboard";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const client = await createApiClient(token);
  const limit = parseInt(req.query.limit as string);
  const enabled = req.query.enabled === "true";

  const trollboardReply = await client.fetch_trollboard(req.query.time_frame as TrollboardTimeFrame, {
    limit,
    enabled,
  });

  trollboardReply.trollboard = updateUsersDisplayNames(trollboardReply.trollboard);
  trollboardReply.trollboard = await updateUsersProfilePictures(trollboardReply.trollboard);

  return res.status(200).json(trollboardReply);
});
