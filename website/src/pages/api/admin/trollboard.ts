import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import { TrollboardTimeFrame } from "src/types/Trollboard";
import { getValidDisplayName } from "src/lib/display_name_validation";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const client = await createApiClient(token);

  const trollboard = await client.fetch_trollboard(req.query.time_frame as TrollboardTimeFrame, {
    limit: req.query.limit as unknown as number,
    enabled: req.query.enabled as unknown as boolean,
  });

  trollboard.trollboard.forEach((troll) => {
    troll.display_name = getValidDisplayName(troll.display_name, troll.username);
  });

  return res.status(200).json(trollboard);
});
