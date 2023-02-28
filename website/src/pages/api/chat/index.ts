import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = new OasstInferenceClient(req, res, token);
  const data = await client.create_chat();
  return res.status(200).json(data);
});

export default handler;
