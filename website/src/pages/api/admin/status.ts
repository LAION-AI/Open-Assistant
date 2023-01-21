import { getToken } from "next-auth/jwt";
import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";

/**
 * Returns tasks availability, stats, and tree manager stats.
 */
const handler = withRole("admin", async (req, res) => {
  const token = await getToken({ req });
  const currentUser = {
    id: token.sub,
    display_name: token.name,
    auth_method: "local",
  };
  const tasksAvailabilityData = await oasstApiClient.fetch_tasks_availability(currentUser);
  const statsData = await oasstApiClient.fetch_stats();
  const treeManagerData = await oasstApiClient.fetch_tree_manager();

  const status = {
    tasksAvailability: tasksAvailabilityData,
    stats: statsData,
    treeManager: treeManagerData,
  };

  res.status(200).json(status);
});

export default handler;
