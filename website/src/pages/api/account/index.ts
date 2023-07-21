import { withoutRole } from "src/lib/auth";
import prisma from "src/lib/prismadb";
import { ExternalProvider, UserAccountResponse } from "src/types/Account";

const handler = withoutRole("banned", async (req, res, token) => {
  const user = await prisma.user.findFirst({
    where: { id: token.sub },
    select: { emailVerified: true, accounts: true },
  });

  const emailIsVerified = Boolean(user.emailVerified);
  const accounts = user.accounts.map(({ provider, providerAccountId }) => ({
    provider: provider as ExternalProvider,
    providerAccountId,
  }));

  const response: UserAccountResponse = { emailIsVerified, accounts };

  return res.status(200).json(response);
});

export default handler;
