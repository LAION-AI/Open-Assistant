import { getToken } from "next-auth/jwt";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";

/**
 * Stores the task interaction with the Task Backend and then returns the next task generated.
 *
 * This implicity does a few things:
 * 1) Stores the answer with the Task Backend.
 * 2) Records the new task in our local database.
 * 3) Returns the newly created task to the client.
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  // Parse out the local task ID and the interaction contents.
  const { id, content, update_type } = await JSON.parse(req.body);

  // Log the interaction locally to create our user_post_id needed by the Task
  // Backend.
  const interaction = await prisma.taskInteraction.create({
    data: {
      content,
      task: {
        connect: {
          id,
        },
      },
    },
  });

  let newTask;
  try {
    newTask = await oasstApiClient.interactTask(update_type, id, interaction.id, content, token);
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
