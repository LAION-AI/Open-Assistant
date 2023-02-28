import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

export default withoutRole("banned", async (req, res, token) => {
  const client = new OasstInferenceClient(req, res, token);
  const { chat_id, message_id, score } = req.body as { chat_id: string; message_id: string; score: number };
  if (score < -1 || score > 1) {
    return res.status(400).send("");
  }

  const data = await client.vote({ message_id, chat_id, score });

  return res.status(200).json(data);
});
