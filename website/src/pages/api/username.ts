import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";
import { getValidDisplayName } from "src/lib/display_name_validation";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const { username } = req.body;
  let { name } = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      name: username,
    },
  });
  name = getValidDisplayName(name, token.sub);
  res.json({ name });
});

export default handler;
