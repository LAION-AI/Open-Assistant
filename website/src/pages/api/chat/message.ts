import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const { chat_id, parent_id, content } = req.body;
  const client = new OasstInferenceClient(req, res, token);
  const responseStream = await client.post_prompt({ chat_id, parent_id, content });
  res.status(200);
  responseStream.pipe(res);
});

export default handler;
