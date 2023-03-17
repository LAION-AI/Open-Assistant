import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = new OasstInferenceClient(req, res, token);
  let data;
  if (req.method === "GET") {
    data = await client.get_message(req.query.chat_id as string, req.query.message_id as string);
  } else if (req.method === "POST") {
    const { chat_id, parent_id, content } = req.body;
    data = await client.post_prompt({ chat_id, parent_id, content });
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
