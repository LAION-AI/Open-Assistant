import { withoutRole } from "src/lib/auth";
import { isSSRChatEnabled } from "src/lib/isChatEnable";
import { createInferenceClient } from "src/lib/oasst_inference_client";
import { GetChatsParams } from "src/types/Chat";

export const PAGE_SIZE = 20;

const handler = withoutRole("banned", async (req, res, token) => {
  if (!isSSRChatEnabled()) {
    return res.status(404).end();
  }
  const client = createInferenceClient(token);

  let data;
  if (req.method === "GET") {
    if (req.query.chat_id) {
      data = await client.get_chat(req.query.chat_id as string);
    } else {
      const params: GetChatsParams = {
        limit: PAGE_SIZE,
      };
      if (req.query.before) {
        params["before"] = req.query.before as string;
      }
      if (req.query.after) {
        params["after"] = req.query.after as string;
      }
      data = await client.get_my_chats(params);
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
