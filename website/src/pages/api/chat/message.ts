import { withoutRole } from "src/lib/auth";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { InferencePostMessageParams } from "src/types/Chat";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = createInferenceClient(token);

  let data;
  if (req.method === "GET") {
    data = await client.get_message(req.query.chat_id as string, req.query.message_id as string);
  } else if (req.method === "POST") {
    data = await client.post_prompt(req.body as InferencePostMessageParams);
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
