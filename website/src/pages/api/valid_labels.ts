import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res) => {
  const valid_labels = await oasstApiClient.fetch_valid_text();
  res.status(200).json(valid_labels);
});

export default handler;
