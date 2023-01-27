import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

/**
 * Returns the set of valid labels that can be applied to messages.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const client = await createApiClient(token);
  const valid_labels = await client.fetch_valid_text();
  res.status(200).json(valid_labels);
});

export default handler;
