import { getToken } from "next-auth/jwt";
import withRole from "src/lib/auth";
import prisma from "src/lib/prismadb";

/**
 * Returns a list of user results from the database when the requesting user is
 * a logged in admin.
 */
const handler = withRole("admin", async (req, res) => {
  // Fetch 20 users.
  const users = await prisma.user.findMany({
    select: {
      id: true,
      role: true,
      name: true,
      email: true,
    },
    take: 20,
  });

  res.status(200).json(users);
});

export default handler;
