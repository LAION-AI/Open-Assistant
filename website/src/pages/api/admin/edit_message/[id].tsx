import { withAnyRole } from "src/lib/auth";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import { getBackendUserCore } from "src/lib/users";

export default withAnyRole(["admin", "moderator"], async (req, res, token) => {
  const { id } = req.query;

  try {
    const user = await getBackendUserCore(token.sub);
    const oasstApiClient = createApiClientFromUser(user);

    await oasstApiClient.edit_message(id as string, user, req.body.arg as string);
    res.status(200).json({ message: "Message edited" });
  } catch (e) {
    res.status(500).json({ message: "Failed to edit message" });
  }
});
