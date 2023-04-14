import type { NextApiRequest, NextApiResponse } from "next";
import { getToken } from "next-auth/jwt";
import { createApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";

export const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const token = await getToken({ req });
  if (!token) {
    return res.status(403).end();
  }

  const client = await createApiClient(token);
  
  prisma.user.delete({ where: { id: token.sub } });
};
