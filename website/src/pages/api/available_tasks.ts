import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const availableTasks = await oasstApiClient.fetch_available_tasks(user);
  res.status(200).json(availableTasks);
});

export default handler;
