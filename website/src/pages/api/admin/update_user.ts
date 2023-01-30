import { withRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";

/**
 * Update's the user's data in the database.  Accessible only to admins.
 */
const handler = withRole("admin", async (req, res, token) => {
  const { id, auth_method, user_id, notes, role } = req.body;

  const oasstApiClient = await createApiClient(token);
  // If the user is authorized by the web, update their role.
  if (auth_method === "local") {
    await prisma.user.update({
      where: { id },
      data: { role },
    });
  }
  // Tell the backend the user's enabled or not enabled status.
  await oasstApiClient.set_user_status(user_id, role !== "banned", notes);

  res.status(200).json({});
});

export default handler;
