import { withRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";
import { BackendUser } from "src/types/Users";

/**
 * The number of users to fetch in a single request.  Could later be a query parameter.
 */
const PAGE_SIZE = 1;

/**
 * Returns a list of user results from the database when the requesting user is
 * a logged in admin.
 *
 * This takes two query params:
 * - `cursor`: A string representing a user's `display_name`.
 * - `direction`: Either "forward" or "backward" representing the pagination
 *   direction.
 */
const handler = withRole("admin", async (req, res) => {
  const { cursor, direction, display_name = "" } = req.query;

  // First, get all the users according to the backend.
  let all_users: BackendUser[] = [];

  if (typeof display_name === "string" && display_name) {
    all_users = await oasstApiClient.fetch_user_by_display_name(display_name);
  } else {
    all_users = await oasstApiClient.fetch_users(PAGE_SIZE, cursor as string, direction === "forward");
  }

  // Next, get all the users stored in the web's auth database to fetch their role.
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
