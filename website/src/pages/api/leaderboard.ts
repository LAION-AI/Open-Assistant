import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const oasstApiClient = await createApiClient(token);
  const backendUser = await getBackendUserCore(token.sub);
  const time_frame = (req.query.time_frame as LeaderboardTimeFrame) ?? LeaderboardTimeFrame.day;
  const includeUserStats = req.query.includeUserStats;

  if (includeUserStats !== "true") {
    const leaderboard = await oasstApiClient.fetch_leaderboard(time_frame, {
      limit: req.query.limit as unknown as number,
    });
    return res.status(200).json(leaderboard);
  }
  const user = await oasstApiClient.fetch_frontend_user(backendUser);

  const [leaderboard, user_stats] = await Promise.all([
    oasstApiClient.fetch_leaderboard(time_frame, {
      limit: req.query.limit as unknown as number,
    }),
    oasstApiClient.fetch_user_stats_window(user.user_id, time_frame, 3),
  ]);

  res.status(200).json({
    ...leaderboard,
    user_stats_window: user_stats?.leaderboard.map((stats) => ({ ...stats, is_window: true })),
  });
});

export default handler;
