import { getToken } from "next-auth/jwt";

const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  const { id } = req.query;

  if (!id) {
    res.status(400).end();
    return;
  }

  const messageRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages/${id}`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
  });

  const message = await messageRes.json();

  if (!message.parent_id) {
    res.status(404).end();
    return;
  }

  const parentRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/messages/${message.parent_id}`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
  });

  const parent = await parentRes.json();

  // Send recieved messages to the client.
  res.status(200).json(parent);
};

export default handler;
