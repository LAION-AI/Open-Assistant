import { withoutRole } from "src/lib/auth";

/**
 * Adds a report for a message
 *
 */
const handler = withoutRole("banned", async (req, res, token) => {
  // Parse out the local message_id, and the interaction contents.
  const { message_id, text } = req.body;

  const interactionRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/text_labels`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "text_labels",
      message_id: message_id,
      labels: [], // Not yet implemented
      text,
      is_report: true,
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
