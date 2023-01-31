import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const oasstApiClient = await createApiClient(token);
  const time_frame = (req.query.time_frame as LeaderboardTimeFrame) ?? LeaderboardTimeFrame.day;
  const info = await oasstApiClient.fetch_leaderboard(time_frame, { limit: req.query.limit as unknown as number });
  res.status(200).json(info);
});

export default handler;
