import { getToken } from "next-auth/jwt";
import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import { getBackendUserCore } from "src/lib/users";

/**
 * Returns tasks availability, stats, and tree manager stats.
 */
const handler = withRole("admin", async (req, res) => {
  const dummyUser = {
    id: "__dummy_user__",
    display_name: "Dummy User",
    auth_method: "local",
  };
  const [tasksAvailabilityOutcome, statsOutcome, treeManagerOutcome] = await Promise.allSettled([
    oasstApiClient.fetch_tasks_availability(dummyUser),
    oasstApiClient.fetch_stats(),
    oasstApiClient.fetch_tree_manager(),
  ]);

  const status = {
    tasksAvailability: tasksAvailabilityOutcome,
    stats: statsOutcome,
    treeManager: treeManagerOutcome,
  };

  res.status(200).json(status);
});

export default handler;
