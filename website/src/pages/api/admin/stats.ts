import { withRole } from "src/lib/auth";

/**
 * Returns the message stats.
 */
const handler = withRole("admin", async (req, res) => {
  const statsRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/stats/`, {
    method: "GET",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
    },
  });

  const stats = await statsRes.json();

  res.status(statsRes.status).json(stats);
});

export default handler;
