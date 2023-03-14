import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const { chat_id, message_id } = req.query;

  const client = new OasstInferenceClient(req, res, token);
  const stream = await client.stream_events({ chat_id: chat_id as string, message_id: message_id as string });
  res.status(200);
  stream.pipe(res);
});

export default handler;
