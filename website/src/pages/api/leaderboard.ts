import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res) => {
  const { leaderboard } = await oasstApiClient.fetch_leaderboard();
  res.status(200).json(
    leaderboard.map(({ display_name, ranking, score }) => ({
      display_name,
      ranking,
      score,
    }))
  );
});

export default handler;
