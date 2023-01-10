import { Prisma } from "@prisma/client";
import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";

const handler = withoutRole("banned", async (req, res) => {
  // Parse out the local task ID and the interaction contents.
  const { id: frontendId, reason } = await JSON.parse(req.body);

  const registeredTask = await prisma.registeredTask.findUniqueOrThrow({ where: { id: frontendId } });

  const task = registeredTask.task as Prisma.JsonObject;
  const id = task.id as string;

  // Update the backend with the rejection
  await oasstApiClient.nackTask(id, reason);

  // Send the results to the client.
  res.status(200).json({});
});

export default handler;
