import { ROLES } from "src/components/RoleSelect";
import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";
import { BackendUserCore } from "src/types/Users";

export default withoutRole("banned", async (req, res, token) => {
  const isModOrAdmin = token.role === ROLES.ADMIN || token.role === ROLES.MODERATOR;

  let user: BackendUserCore;
  // uid query param is only allowed for moderators and admins else it will be ignored and the user's own stats will be returned
  if (req.query.id && isModOrAdmin) {
    const { id, auth_method, display_name } = req.query;
    user = { id, auth_method, display_name } as BackendUserCore;
  } else {
    if (!token.backendUserId) {
      // user has not yet accepted the terms of service, and therefor does not yet exist in the backend
      /// skip the request entirely
      return res.status(200).json({});
    }

    user = await getBackendUserCore(token.sub);
  }

  const oasstApiClient = createApiClientFromUser(user);
  const stats = await oasstApiClient.fetch_user_stats(user);
  res.status(200).json(stats);
});
