import { withoutRole } from "src/lib/auth";
import { createInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = createInferenceClient(token);

  let data;
  if (req.method === "GET") {
    data = await client.get_message(req.query.chat_id as string, req.query.message_id as string);
  } else if (req.method === "POST") {
    const { chat_id, parent_id, content, work_parameters } = req.body;
    data = await client.post_prompt({ chat_id, parent_id, content, work_parameters });
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
