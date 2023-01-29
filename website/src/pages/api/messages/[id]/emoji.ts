import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

const handler = withoutRole("banned", async (req, res, token) => {
  const { id } = req.query;

  if (!id) {
    res.status(400).end();
    return;
  }

  const messageId = id as string;

  const { emoji, op } = req.body;

  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  try {
    await oasstApiClient.set_user_message_emoji(messageId, user, emoji, op);
  } catch (err) {
    console.error(JSON.stringify(err));
    return res.status(500).json(err);
  }

  // Get updated emoji
  const message = await oasstApiClient.fetch_message(messageId, user);
  res.status(200).json({ emojis: message.emojis, user_emojis: message.user_emojis });
});

export default handler;
