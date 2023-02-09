import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  const stats = await oasstApiClient.fetch_user_stats(user);
  res.status(200).json(stats);
});

export default handler;
