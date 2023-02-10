import { withAnyRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";

/**
 * Returns tasks availability, stats, and tree manager stats.
 */
const handler = withAnyRole(["admin", "moderator"], async (req, res) => {
  // NOTE: why are we using a dummy user here?
  const dummyUser = {
    id: "__dummy_user__",
    display_name: "Dummy User",
    auth_method: "local",
  };
  const oasstApiClient = createApiClientFromUser(dummyUser);
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
