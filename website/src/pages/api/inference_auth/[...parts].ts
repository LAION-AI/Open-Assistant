import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
import { InferenceTokenResponse } from "src/types/Chat";

export default async function inferenceAuthCallback(req: NextApiRequest, res: NextApiResponse) {
  const { code, parts } = req.query;
  console.log(req.query);
  if (!Array.isArray(parts) || parts.length !== 1) {
    return res.status(400).end();
  }
  const [provider] = parts as string[];
  const url = process.env.INFERENCE_SERVER_HOST + `/auth/callback/${provider}?code=${code}`;
  const { data } = await axios<InferenceTokenResponse>(url);
  console.log(data);
  return res.send(data);
}
