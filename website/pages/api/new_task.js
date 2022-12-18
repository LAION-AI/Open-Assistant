import { unstable_getServerSession } from "next-auth/next";
import { authOptions } from "pages/api/auth/[...nextauth]";

/**
 * Returns a new task created from the Task Backend.  We do a few things here:
 *
 * 1) Get the task from the backend and register the requesting user.
 * 2) Store the task in our local database.
 * 3) Send and Ack to the Task Backend with our local id for the task.
 * 4) Return everything to the client.
 */
export default async (req, res) => {
  const session = await unstable_getServerSession(req, res, authOptions);

  // Return nothing if the user isn't registered.
  if (!session) {
    res.status(401).end();
    return;
  }

  // Fetch the new task.
  //
  // This needs to be refactored into an easier to use library.
  const taskRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/tasks/`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "rate_summary",
      user: {
        id: session.user.id,
        display_name: session.user.name,
        auth_method: "local",
      },
    }),
  });
  const task = await taskRes.json();

  // Store the task and link it to the user..
  const registeredTask = await prisma.registeredTask.create({
    data: {
      task,
      user: {
        connect: {
          id: session.user.id,
        },
      },
    },
  });

  // Update the backend with our Task ID
  const ackRes = await fetch(
    `${process.env.FASTAPI_URL}/api/v1/tasks/${task.id}/ack`,
    {
      method: "POST",
      headers: {
        "X-API-Key": process.env.FASTAPI_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        post_id: registeredTask.id,
      }),
    }
  );
  const ack = await ackRes.json();

  // Send the results to the client.
  res.status(200).json(registeredTask);
};
