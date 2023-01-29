import { withoutRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

/**
 * Adds a report for a message
 *
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // Parse out the local message_id, and the interaction contents.
  const { message_id, text } = req.body;

  const user = await getBackendUserCore(token.sub);
  const oasstApiClient = createApiClientFromUser(user);
  try {
    await oasstApiClient.send_report(message_id, user, text);
  } catch (err) {
    console.error(JSON.stringify(err));
    return res.status(500).json(err);
  }

  res.status(200).end();
});

export default handler;
