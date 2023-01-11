import { withoutRole } from "src/lib/auth";

/**
 * Sets the Label in the Backend.
 *
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // Parse out the local message_id, task ID and the interaction contents.
  const { message_id, label_map, text } = await JSON.parse(req.body);

  const interactionRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/text_labels`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "text_labels",
      message_id: message_id,
      labels: label_map,
      text: text,
      user: {
        id: token.sub,
        display_name: token.name || token.email,
        auth_method: "local",
      },
    }),
  });
  res.status(interactionRes.status).end();
});

export default handler;
