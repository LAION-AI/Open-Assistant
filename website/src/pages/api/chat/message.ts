import { withoutRole } from "src/lib/auth";
import { isSSRChatEnabled } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isSSRChatEnabled()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);

  const data = await client.get_message(req.query.chat_id as string, req.query.message_id as string);
  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
