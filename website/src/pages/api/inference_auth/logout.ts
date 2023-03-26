import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";

export default withoutRole("banned", async (req, res, token) => {
  // use delete many until prisma supports "if exists"
  // https://github.com/prisma/prisma/issues/9460
  await prisma.inferenceCredentials.deleteMany({ where: { userId: token.sub } });
  // note: maybe we want to communicate something to the inference backend?
  // like revoking tokens and such?
  return res.redirect(`/chat`);
});
