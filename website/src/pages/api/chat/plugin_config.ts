import { withoutRole } from "src/lib/auth";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { PluginEntry } from "src/types/Chat";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isChatEnable()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);
  const { plugin } = req.body as { plugin: PluginEntry };

  const data = await client.get_plugin_config({ plugin });
  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
