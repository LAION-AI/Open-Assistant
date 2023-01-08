import { getToken } from "next-auth/jwt";
import prisma from "src/lib/prismadb";

/**
 * Update's the user's data in the database.  Accessible only to admins.
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered or if the user isn't an admin.
  if (!token || token.role !== "admin") {
    res.status(403).end();
    return;
  }

  const { id, role } = JSON.parse(req.body);
  await prisma.user.update({
    where: {
      id,
    },
    data: {
      role,
    },
  });

  res.status(200).end();
};

export default handler;
