import withRole from "src/lib/auth";
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
  const skip = parseInt(pageIndex as string) * PAGE_SIZE || 0;

  // Fetch 20 users.
  const users = await prisma.user.findMany({
    select: {
      id: true,
      role: true,
      name: true,
      email: true,
    },
    skip,
    take: PAGE_SIZE,
  });

  res.status(200).json(users);
});

export default handler;
