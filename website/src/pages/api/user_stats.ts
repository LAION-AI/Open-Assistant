import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  let userid: string;
  if (req.query.uid) {
    userid = typeof req.query.uid === "string" ? req.query.uid : req.query.uid[0];
  } else {
    userid = token.sub;
  }

  const user = await getBackendUserCore(userid as string);
  const oasstApiClient = createApiClientFromUser(user);
  const stats = await oasstApiClient.fetch_user_stats(user);
  res.status(200).json(stats);
});

export default handler;
