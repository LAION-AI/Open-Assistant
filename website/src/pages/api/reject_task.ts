import { Prisma } from "@prisma/client";
import { withoutRole } from "src/lib/auth";
import { createApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";

const handler = withoutRole("banned", async (req, res, token) => {
  // Parse out the local task ID and the interaction contents.
  const { id: frontendId } = req.body;

  const [oasstApiClient, registeredTask] = await Promise.all([
    createApiClient(token),
    prisma.registeredTask.findUniqueOrThrow({ where: { id: frontendId } }),
  ]);

  const taskId = (registeredTask.task as Prisma.JsonObject).id as string;

  // Update the backend with the rejection
  await oasstApiClient.nackTask(taskId);

  // Send the results to the client.
  res.status(200).json({});
});

export default handler;
