import { withoutRole } from "src/lib/auth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  const client = new OasstInferenceClient(req, res, token);
  let data;
  if (req.method === "GET") {
    data = await client.get_my_chats();
  } else if (req.method === "POST") {
    data = await client.create_chat();
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
