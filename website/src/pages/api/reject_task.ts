import { Prisma } from "@prisma/client";
import { getToken } from "next-auth/jwt";
import { oasstApiClient } from "src/lib/oasst_api_client";

const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  // Parse out the local task ID and the interaction contents.
  const { id: frontendId, reason } = await JSON.parse(req.body);

  const registeredTask = await prisma.registeredTask.findUniqueOrThrow({ where: { id: frontendId } });

  const task = registeredTask.task as Prisma.JsonObject;
  const id = task.id as string;

  // Update the backend with the rejection
  await oasstApiClient.nackTask(id, reason);

  // Send the results to the client.
  res.status(200).json({});
};

export default handler;
