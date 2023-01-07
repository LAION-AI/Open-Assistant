import { getToken } from "next-auth/jwt";
import client from "src/lib/prismadb";

/**
 * Returns a list of user results from the database when the requesting user is
 * a logged in admin.
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered or if the user isn't an admin.
  if (!token || token.role !== "admin") {
    res.status(403).end();
    return;
  }

  // Fetch 20 users.
  const users = await client.user.findMany({
    select: {
      id: true,
      role: true,
      name: true,
      email: true,
    },
    take: 20,
  });

  res.status(200).json(users);
};

export default handler;
