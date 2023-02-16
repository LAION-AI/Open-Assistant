import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";

const handler = withoutRole("banned", async (req, res, token) => {
  try {
    const client = await createApiClient(token);
    const data = await client.fetch_cached_stats();
    res.status(200).json(data);
  } catch (e) {
    res.status(500).json({ error: "Error fetching stats" });
  }
});

export default handler;
