import { unstable_getServerSession } from "next-auth/next";
import { authOptions } from "./auth/[...nextauth]";

/**
 * Returns a list of prompts from the Labeler Backend.
 */
export default async (req, res) => {
  const session = await unstable_getServerSession(req, res, authOptions);

  if (!session) {
    res.status(401).end();
    return;
  }

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

  res.status(200).json(registeredTask);
};
