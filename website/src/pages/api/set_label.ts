import { getToken } from "next-auth/jwt";
import prisma from "src/lib/prismadb";

/**
 * Sets the Label in the Backend.
 *
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }
 console.log(JSON.parse(req.body));
  // Parse out the local task ID and the interaction contents.
  const { post_id, label_map, text } = await JSON.parse(req.body);
  console.log(JSON.stringify(
      {
        "type": "text_labels",
        "message_id": post_id,
        "labels": label_map,
        "text": text,
        "user": {
          "id": token.sub,
          "display_name": token.name || token.email,
          "auth_method": "local",
        }}));
  console.log("Here sending text_labels1...");
  // Send the interaction to the Text Label to the Backend.
  const interactionRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/text_labels`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
        "type": "text_labels",
        "message_id": post_id,
        "labels": label_map,
        "text": text,
        "user": {
          "id": token.sub,
          "display_name": token.name || token.email,
          "auth_method": "local",
        }

    }),
  });
  console.log(interactionRes);
  res.status(interactionRes.status).json(interactionRes.json());
};

export default handler;
