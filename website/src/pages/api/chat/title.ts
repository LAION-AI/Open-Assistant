import { withoutRole } from "src/lib/auth";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isChatEnable()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const { chat_id, title } = req.body as { chat_id: string; title: string };

  await client.update_chat({ chat_id, title });

  res.status(200).end();
});

export default handler;
