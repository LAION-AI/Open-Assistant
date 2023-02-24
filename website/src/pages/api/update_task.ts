import { Prisma } from "@prisma/client";
import { withoutRole } from "src/lib/auth";
import { getLanguageFromRequest } from "src/lib/languages";
import { createApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { getBackendUserCore } from "src/lib/users";

/**
 * Stores the task interaction with the Task Backend and then returns the next task generated.
 *
 * This implicitly does a few things:
 * 1) Records the users answer in our local database.
 * 2) Accepts the task.
 * 3) Sends the users answer to the Task Backend.
 * 4) Records the new task in our local database.
 * 5) Returns the newly created task to the client.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // Parse out the local task ID and the interaction contents.
  const { id: frontendId, content, update_type } = req.body;

  const lang = getLanguageFromRequest(req);

  // do in parallel since they are independent
  const [_, registeredTask, oasstApiClient] = await Promise.all([
    // Record that the user has done meaningful work and is no longer new.
    prisma.user.update({ where: { id: token.sub }, data: { isNew: false } }),
    // Accept the task so that we can complete it, this will probably go away soon.
    prisma.registeredTask.findUniqueOrThrow({ where: { id: frontendId } }),
    // Create client for upcoming requests
    createApiClient(token),
  ]);

  const taskId = (registeredTask.task as Prisma.JsonObject).id as string;

  await oasstApiClient.ackTask(taskId, registeredTask.id);

  // Log the interaction locally to create our user_post_id needed by the Task
  // Backend.
  const interaction = await prisma.taskInteraction.create({
    data: {
      content,
      task: {
        connect: {
          id: frontendId,
        },
      },
    },
  });

  const user = await getBackendUserCore(token.sub);
  try {
    await oasstApiClient.interactTask(update_type, taskId, frontendId, interaction.id, content, user!, lang);
    return res.status(204).send("");
  } catch (err: unknown) {
    console.error(JSON.stringify(err));
    return res.status(500).json(err);
  }
});

export default handler;
