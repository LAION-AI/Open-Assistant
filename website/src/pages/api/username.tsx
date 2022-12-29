import { getSession } from "next-auth/react";
import { Prisma } from "@prisma/client";
import Email from "next-auth/providers/email";

// POST /api/post
// Required fields in body: title
// Optional fields in body: content
export default async function handle(req, res) {
  const { username } = req.body;
  const { email } = req.body;

  const session = await getSession({ req });
  const result = await prisma.user.update({
    where: {
      email: session.user.email,
    },
    data: {
      name: username,
    },
  });
  res.json({ name: result.name });
}
