import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore, getUserLanguage } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  const userLanguage = getUserLanguage(req);
  const availableTasks = await oasstApiClient.fetch_available_tasks(user, userLanguage);
  res.status(200).json(availableTasks);
});

export default handler;
