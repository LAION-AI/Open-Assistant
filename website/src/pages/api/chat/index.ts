import { withoutRole } from "src/lib/auth";
import { createInferenceAccessors } from "src/lib/oasst_inference_auth";

const handler = withoutRole("banned", async (req, res, token) => {
  const { client } = createInferenceAccessors(req, res);

  let data;
  if (req.method === "GET") {
    if (req.query.chat_id) {
      data = await client.get_chat(req.query.chat_id as string);
    } else {
      data = await client.get_my_chats();
    }
  } else if (req.method === "POST") {
    data = await client.create_chat();
  }

  if (data) {
    return res.status(200).json(data);
  }
  res.status(400).end();
});

export default handler;
