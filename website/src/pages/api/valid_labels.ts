import { getToken } from "next-auth/jwt";
import { oasstApiClient } from "src/lib/oasst_api_client";

/**
 * TODO
 */
const handler = async (req, res) => {
  const token = await getToken({ req });

  // Return nothing if the user isn't registered.
  if (!token) {
    res.status(401).end();
    return;
  }

  // Fetch the new task.
  const valid_labels = await oasstApiClient.fetch_valid_text();

  // Send the results to the client.
  res.status(200).json(valid_labels);
};

export default handler;
