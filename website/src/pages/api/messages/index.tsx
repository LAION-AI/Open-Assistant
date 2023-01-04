import { getToken } from "next-auth/jwt";

const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  const messagesRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });
  const messages = await messagesRes.json();

  // Send recieved messages to the client.
  res.status(200).json(messages);
};

export default handler;
