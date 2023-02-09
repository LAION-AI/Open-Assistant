import { withoutRole } from "src/lib/auth";

/**
 * Sets the Label in the Backend.
 *
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // TODO: move to oasst_api_client
  // Parse out the local message_id, and the interaction contents.
  const { message_id, label_map } = req.body;

  const interactionRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/text_labels/`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "text_labels",
      message_id: message_id,
      labels: label_map,
      text: "", // used only in reporting
      is_report: false,
      user: {
        id: token.sub,
        display_name: token.name || token.email,
        auth_method: "local",
      },
    }),
  });
  if (interactionRes.status !== 204) {
    const r = await interactionRes.json();
    console.error(JSON.stringify(r));
  }
  res.status(interactionRes.status).end();
});

export default handler;
