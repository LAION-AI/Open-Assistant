import { withoutRole } from "src/lib/auth";
import { updateUsersDisplayNames, updateUsersProfilePictures } from "src/lib/leaderboard_utilities";
import { createApiClient } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

export default withoutRole("banned", async (req, res, token) => {
  if (!token.backendUserId) {
    // user has not yet accepted the terms of service, and therefor does not yet exist in the backend
    /// skip the request entirely
    return res.status(200).json(null);
  }

  const oasstApiClient = await createApiClient(token);
  const backendUser = await getBackendUserCore(token.sub);
  const time_frame = (req.query.time_frame as LeaderboardTimeFrame) ?? LeaderboardTimeFrame.day;
  const limit = parseInt(req.query.limit as string);
  const includeUserStats = req.query.includeUserStats === "true";

  if (!includeUserStats) {
    const leaderboardReply = await oasstApiClient.fetch_leaderboard(time_frame, { limit });
    leaderboardReply.leaderboard = updateUsersDisplayNames(leaderboardReply.leaderboard);
    leaderboardReply.leaderboard = await updateUsersProfilePictures(leaderboardReply.leaderboard);
    return res.status(200).json(leaderboardReply);
  }
  const user = await oasstApiClient.fetch_frontend_user(backendUser);

  const [leaderboardReply, user_stats] = await Promise.all([
    oasstApiClient.fetch_leaderboard(time_frame, { limit }),
    oasstApiClient.fetch_user_stats_window(user.user_id, time_frame, 3),
  ]);

  leaderboardReply.leaderboard = updateUsersDisplayNames(leaderboardReply.leaderboard);
  leaderboardReply.leaderboard = await updateUsersProfilePictures(leaderboardReply.leaderboard);

  res.status(200).json({
    ...leaderboardReply,
    user_stats_window: user_stats?.leaderboard.map((stats) => ({ ...stats, is_window: true })),
  });
});
