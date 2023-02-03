import { withoutRole } from "src/lib/auth";
import { ERROR_CODES } from "src/lib/constants";
import { OasstError } from "src/lib/oasst_api_client";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { getBackendUserCore, getUserLanguage } from "src/lib/users";

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
  const userLanguage = getUserLanguage(req);

  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  let task;
  try {
    task = await oasstApiClient.fetchTask(task_type as string, user, userLanguage);
  } catch (err) {
    if (err instanceof OasstError && err.errorCode === ERROR_CODES.TASK_REQUESTED_TYPE_NOT_AVAILABLE) {
      res.status(503).json({});
    } else {
      console.error(err);
      res.status(500).json(err);
    }
    return;
  }

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

  // Send the results to the client.
  res.status(200).json(registeredTask);
});

export default handler;
