import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res) => {
  const time_frame = (req.query.time_frame as LeaderboardTimeFrame) || LeaderboardTimeFrame.day;
  const { leaderboard } = await oasstApiClient.fetch_leaderboard(time_frame);
  res.status(200).json(leaderboard);
});

export default handler;
