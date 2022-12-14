import { unstable_getServerSession } from "next-auth/next";
import { authOptions } from "./auth/[...nextauth]";

export default async (req, res) => {
  const session = await unstable_getServerSession(req, res, authOptions);

  if (!session) {
    res.status(200).json([{ name: "cat" }]);
    return;
  }
  const promptRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/prompts`, {
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });
  const prompts = await promptRes.json();

  res.status(200).json(prompts);
};
