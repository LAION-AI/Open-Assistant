import { withoutRole } from "src/lib/auth";
import { isValidDisplayName } from "src/lib/display_name_validation";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const { username } = req.body;
  if (!isValidDisplayName(username)) {
    return res.status(400).json({ message: "Invalid username" });
  }

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
