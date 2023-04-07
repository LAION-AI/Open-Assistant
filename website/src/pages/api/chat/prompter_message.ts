import { withoutRole } from "src/lib/auth";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { InferencePostPrompterMessageParams } from "src/types/Chat";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isChatEnable()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);

  const data = await client.post_prompter_message(req.body as InferencePostPrompterMessageParams);

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
