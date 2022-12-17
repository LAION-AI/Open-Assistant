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

  const { id, content } = await JSON.parse(req.body);

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
  console.log(interactionRes.status);
  const newTask = await interactionRes.json();
  console.log(newTask);

  res.status(200).json(newTask);
};
