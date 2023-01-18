import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const { username } = req.body;
  const { name } = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      name: username,
    },
  });
  res.json({ name });
});

export default handler;
