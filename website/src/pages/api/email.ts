import { withoutRole } from "src/lib/auth";
import { isValidEmail } from "src/lib/email_validation";
import prisma from "src/lib/prismadb";

/**
 * Updates the user's `name` field in the `User` table.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  const newmail = req.body.email;
  if (!isValidEmail(newmail)) {
    return res.status(400).json({ message: "Invalid email" });
  }

  const emailExists = await prisma.user.findFirst({
    where: {
      email: newmail,
    },
  });
  if (emailExists) {
    console.log("this email exists.");
    return res.status(400).json({ message: "Invalid email" });
  }

  const { email } = await prisma.user.update({
    where: {
      id: token.sub,
    },
    data: {
      email: newmail,
    },
  });
  res.json({ newmail });
});

export default handler;
