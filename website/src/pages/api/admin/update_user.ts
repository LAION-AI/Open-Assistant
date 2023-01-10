import withRole from "src/lib/auth";
import prisma from "src/lib/prismadb";

/**
 * Update's the user's data in the database.  Accessible only to admins.
 */
const handler = withRole("admin", async (req, res) => {
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
});

export default handler;
