import { withRole } from "src/lib/auth";

/**
 * Returns the messages recorded by the backend for a user.
 */
const handler = withRole("admin", async (req, res) => {
  const treeManagerRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/stats/tree_manager`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });
  const treeManager = await treeManagerRes.json();

  res.status(treeManagerRes.status).json(treeManager);
});

export default handler;
