import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's paper ack info
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
    return res.status(200).json(user);
  }

  const { paperackYes, paperackName } = req.body;

  const user = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      paperackYes,
      paperackName,
    },
    select: {
      paperackYes: true,
      paperackName: true,
    },
  });
  return res.status(200).json(user);
});

export default handler;
