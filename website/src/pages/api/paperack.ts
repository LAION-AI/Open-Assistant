import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // handle GET
  if (req.method === "GET") {
    const user = await prisma.user.findUnique({
      where: {
        id: token.sub,
      },
      select: {
        paperackYes: true,
        paperackName: true,
      },
    });
    res.json(user);
    return;
  }

  const { paperackYes, paperackName } = req.body;

  const udpates = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      paperackYes,
      paperackName,
    },
  });
  res.json(udpates);
});

export default handler;
