import { getToken } from "next-auth/jwt";

const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  const { id } = req.query;

  const messageRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages/${id}`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
  });
  const message = await messageRes.json();

  // Send recieved messages to the client.
  res.status(200).json(message);
};

export default handler;
