import { unstable_getServerSession } from "next-auth/next";
import { authOptions } from "./auth/[...nextauth]";

/**
 * Stores the task interaction with the Task Backend and then returns the next task generated.
 *
 * This implicity does a few things:
 * 1) Stores the answer with the Task Backend.
 * 2) Records the new task in our local database.
 * 3) (TODO) Acks the new task with our local task ID to the Task Backend.
 * 4) Returns the newly created task to the client.
 */
export default async (req, res) => {
  const session = await unstable_getServerSession(req, res, authOptions);

  // Return nothing if the user isn't registered.
  if (!session) {
    res.status(401).end();
    return;
  }

  // Parse out the local task ID and the interaction contents.
  const { id, content } = await JSON.parse(req.body);

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

  // Send the interaction to the Task Backend.  This automatically fetches the
  // next task in the sequence (or the done task).
  const interactionRes = await fetch(
    `${process.env.FASTAPI_URL}/api/v1/tasks/interaction`,
    {
      method: "POST",
      headers: {
        "X-API-Key": process.env.FASTAPI_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: "post_rating",
        user: {
          id: session.user.id,
          display_name: session.user.name,
          auth_method: "local",
        },
        post_id: id,
        user_post_id: interaction.id,
        ...content,
      }),
    }
  );
  const newTask = await interactionRes.json();

  // Stores the new task with our database.
  const newRegisteredTask = await prisma.registeredTask.create({
    data: {
      task: newTask,
      user: {
        connect: {
          id: session.user.id,
        },
      },
    },
  });

  // TODO: Ack the task with the Task Backend using the newly created local
  // task ID.

  // Send the next task in the sequence to the client.
  res.status(200).json(newRegisteredTask);
};
