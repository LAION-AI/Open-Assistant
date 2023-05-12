import { withoutRole } from "src/lib/auth";
import { isSSRChatEnabled } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

export default withoutRole("banned", async (req, res, token) => {
  if (!isSSRChatEnabled()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const { chat_id, message_id, active } = req.body as { chat_id: string; message_id: string; active: boolean };

  const data = await client.sibling_active({ chat_id, message_id, active });
  return res.status(200).json(data);
});
