import { withoutRole } from "src/lib/auth";
import { isChatEnable } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isChatEnable()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);

  let data;
  if (req.method === "GET") {
    if (req.query.chat_id) {
      data = await client.get_chat(req.query.chat_id as string);
    } else {
      data = await client.get_my_chats();
    }
  } else if (req.method === "POST") {
    data = await client.create_chat();
  } else if (req.method === "DELETE") {
    // TODO: re-activate later
    // await client.delete_chat(req.query.chat_id as string);
    data = {};
  } else if (req.method === "PUT") {
    await client.update_chat(req.body);
    return res.status(200).end();
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
