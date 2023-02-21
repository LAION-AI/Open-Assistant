import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { TrollboardTimeFrame } from "src/types/Trollboard";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const client = await createApiClient(token);

  const trollboard = await client.fetch_trollboard(req.query.time_frame as TrollboardTimeFrame, {
    limit: req.query.limit as unknown as number,
  });

  return res.status(200).json(trollboard);
});
