import { post } from "src/lib/api";
import { withoutRole } from "src/lib/auth";

export const INFERENCE_HOST = process.env.INFERENCE_SERVER_HOST;

const handler = withoutRole("banned", async (req, res, token) => {
  const chat = await post(INFERENCE_HOST + "/chat", { arg: {} });
  return res.status(200).json(chat);
});

export default handler;
