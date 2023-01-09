import { Prisma } from "@prisma/client";
import { getToken } from "next-auth/jwt";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";

/**
 * Stores the task interaction with the Task Backend and then returns the next task generated.
 *
 * This implicity does a few things:
 * 1) Records the users answer in our local database.
 * 2) Accepts the task.
 * 3) Sends the users answer to the Task Backend.
 * 4) Records the new task in our local database.
 * 5) Returns the newly created task to the client.
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  // Parse out the local task ID and the interaction contents.
  const { id: frontendId, content, update_type } = await JSON.parse(req.body);

  // Accept the task so that we can complete it, this will probably go away soon.
  const registeredTask = await prisma.registeredTask.findUniqueOrThrow({ where: { id: frontendId } });
  const task = registeredTask.task as Prisma.JsonObject;
  const id = task.id as string;
  await oasstApiClient.ackTask(id, registeredTask.id);

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

  let newTask;
  try {
    newTask = await oasstApiClient.interactTask(update_type, frontendId, interaction.id, content, token);
  } catch (err) {
    return res.status(500).json(err);
  }

  // Stores the new task with our database.
  const newRegisteredTask = await prisma.registeredTask.create({
    data: {
      task: newTask,
      user: {
        connect: {
          id: token.sub,
        },
      },
    },
  });

  // Send the next task in the sequence to the client.
  res.status(200).json(newRegisteredTask);
};

export default handler;
