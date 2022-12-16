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
  try {
    const promptRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/prompts`, {
      headers: {
        "X-API-Key": process.env.FASTAPI_KEY,
      },
    });
    const prompts = await promptRes.json();

    res.status(200).json(prompts);
  } catch (error) {
    console.error(error);
    res.status(500);
  }
  res.end();
};
