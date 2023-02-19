import axios from "axios";
import { IncomingMessage } from "http";
import { withoutRole } from "src/lib/auth";

import { INFERENCE_HOST } from ".";

const handler = withoutRole("banned", async (req, res, token) => {
  const { chat_id, parent_id, content } = req.body;

  const { data } = await axios.post<IncomingMessage>(
    INFERENCE_HOST + `/chat/${chat_id}/message`,
    { parent_id, content },
    { responseType: "stream" }
  );
  res.status(200);
  data.pipe(res);
});

export default handler;
