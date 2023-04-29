import { withoutRole } from "src/lib/auth";
import { isSSRChatEnabled } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

export default withoutRole("banned", async (req, res, token) => {
  if (!isSSRChatEnabled()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const { chat_id, message_id, score } = req.body as { chat_id: string; message_id: string; score: number };
  if (![-1, 0, 1].includes(score)) {
    return res.status(400).send("Invalid score");
  }

  const data = await client.vote({ message_id, chat_id, score });
  return res.status(200).json(data);
});
