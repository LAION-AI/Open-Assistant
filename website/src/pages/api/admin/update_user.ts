import { ROLES } from "src/components/RoleSelect";
import { withAnyRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";

/**
 * Update's the user's data in the database.  Accessible only to admins.
 */
const handler = withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const { id, user_id, notes, role, show_on_leaderboard } = req.body;
  // mod can't update user role to mod or admin
  if (token.role === ROLES.MODERATOR && (role === ROLES.MODERATOR || role === ROLES.ADMIN)) {
    return res.status(403).json({});
  }
  const oasstApiClient = await createApiClient(token);
  await prisma.user.update({
    where: { id },
    data: { role },
  });

  // Tell the backend the user's enabled or not enabled status.
  await oasstApiClient.set_user_status(user_id, role !== "banned", notes, show_on_leaderboard);

  res.status(200).json({});
});

export default handler;
