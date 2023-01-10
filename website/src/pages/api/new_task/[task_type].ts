import { withoutRole } from "src/lib/auth";
import { oasstApiClient } from "src/lib/oasst_api_client";
import prisma from "src/lib/prismadb";

/**
 * Returns a new task created from the Task Backend.  We do a few things here:
 *
 * 1) Get the task from the backend and register the requesting user.
 * 2) Store the task in our local database.
 * 3) Send and Ack to the Task Backend with our local id for the task.
 * 4) Return everything to the client.
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // Fetch the new task.
  const { task_type } = req.query;
  const task = await oasstApiClient.fetchTask(task_type as string, token);
  const valid_labels = await oasstApiClient.fetch_valid_text();

  // Store the task and link it to the user..
  const registeredTask = await prisma.registeredTask.create({
    data: {
      task,
      user: {
        connect: {
          id: token.sub,
        },
      },
    },
  });

  // Add the valid labels that can be used to flag messages in this Task
  registeredTask["valid_labels"] = valid_labels;

  // Send the results to the client.
  res.status(200).json(registeredTask);
});

export default handler;
