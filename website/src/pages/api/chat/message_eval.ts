import { withoutRole } from "src/lib/auth";
import { isSSRChatEnabled } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

export default withoutRole("banned", async (req, res, token) => {
  if (!isSSRChatEnabled()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const { chat_id, message_id, inferior_message_ids } = req.body as {
    chat_id: string;
    message_id: string;
    inferior_message_ids: string[];
  };

  const data = await client.message_eval({ chat_id, message_id, inferior_message_ids });
  return res.status(200).json(data);
});
