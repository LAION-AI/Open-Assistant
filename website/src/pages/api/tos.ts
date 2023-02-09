import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  if (req.method === "GET") {
    const tos_acceptance_date = await oasstApiClient.fetch_tos_acceptance(user);
    return res.status(200).json(tos_acceptance_date);
  } else if (req.method === "POST") {
    await oasstApiClient.set_tos_acceptance(user);
    return res.status(200).end();
  }
  res.status(400).end();
});

export default handler;
