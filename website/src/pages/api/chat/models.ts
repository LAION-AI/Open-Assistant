import { withoutRole } from "src/lib/auth";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isChatEnable()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const models = await client.get_models();

  return res.status(200).json(models);
});

export default handler;
