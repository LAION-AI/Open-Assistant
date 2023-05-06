import { AxiosError } from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
import { getToken } from "next-auth/jwt";
import { logger } from "src/lib/logger";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import prisma from "src/lib/prismadb";
import { getBackendUserCore } from "src/lib/users";

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const token = await getToken({ req });
  if (!token) {
    return res.status(403).end();
  }

  if (req.method !== "DELETE") {
    return res.status(400).end();
  }

  logger.info("deleting user", token.sub);
  try {
    const backendUserCore = await getBackendUserCore(token.sub);
    const client = createApiClientFromUser(backendUserCore);
    await client.delete_account(backendUserCore);
    logger.info(`user ${token.sub} deleted from data backend`);
  } catch (err) {
    logger.info("could not delete user from data backend", err);
    return res.status(500).end();
  }

  try {
    const client = createInferenceClient(token);
    await client.delete_account();
    logger.info(`user ${token.sub} deleted from inference`);
  } catch (err) {
    if (err instanceof AxiosError && err.response.status === 404) {
      // user does not exist in the inference backend, they have not send any chats
      // that is okay, we can continue
      logger.info(`user ${token.sub} does not exist on inference`);
    } else {
      logger.info("could not delete user from inference backend", err);
      // we don't return here, the other account is already deleted, we have to power through it
    }
  }

  try {
    await prisma.user.delete({ where: { id: token.sub } });
    logger.info(`user ${token.sub} deleted from webdb`);
  } catch (err) {
    console.error("could not delete user from webdb", err);
    // we don't return here, the other account is already deleted, we have to power through
  }
  return res.status(200).end();
};

export default handler;
