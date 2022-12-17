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

  const { id, rating } = await JSON.parse(req.body);

  const registeredTask = await prisma.registeredTask.findUnique({
    where: { id },
    select: { task: true },
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
        type: "text_reply_to_post",
        user: {
          id: session.user.id,
          display_name: session.user.name,
          auth_method: "local",
        },
        post_id: id,
        user_post_id: "1234",
        text: rating,
      }),
    }
  );
  console.log(interactionRes.status);
  const interaction = await interactionRes.json();
  console.log(interaction);

  res.status(200).end();
};
