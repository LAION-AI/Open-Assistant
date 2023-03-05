import { withoutRole } from "src/lib/auth";
import { getLanguageFromRequest } from "src/lib/languages";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user!);
  const userLanguage = getLanguageFromRequest(req);
  const availableTasks = await oasstApiClient.fetch_available_tasks(user!, userLanguage);
  res.status(200).json(availableTasks);
});

export default handler;
