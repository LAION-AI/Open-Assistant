import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";

// The number of users to fetch in any request.
const PAGE_SIZE = 20;

/**
 * Returns a list of user results from the database when the requesting user is
 * a logged in admin.
 */
const handler = withRole("admin", async (req, res) => {
  // Figure out the pagination index and skip that number of users.
  //
  // Note: with Prisma this isn't the most efficient but it's the only possible
  // option with cuid based User IDs.
  const { pageIndex } = req.query;

  // First, get all the users according to the backend.
  const all_users = await oasstApiClient.fetch_users(20);

  // Next, get all the users stored in the web's auth datbase to fetch their role.
  const local_user_ids = all_users.map(({ id }) => id);
  const local_users = await prisma.user.findMany({
    where: {
      id: {
        in: local_user_ids,
      },
    },
    select: {
      id: true,
      role: true,
    },
  });

  // Combine the information by updating the set of full users with their role.
  // Default any users without a role set locally as "general".
  const local_user_map = local_users.reduce((result, user) => {
    result.set(user.id, user.role);
    return result;
  }, new Map());

  const users = all_users.map((user) => {
    const role = local_user_map.get(user.id) || "general";
    return {
      ...user,
      role,
    };
  });

  res.status(200).json(users);
});

export default handler;
