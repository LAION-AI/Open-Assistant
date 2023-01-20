import { withRole } from "src/lib/auth";

/**
 * Returns result of tasks availability query using a dummy user.
 */
const handler = withRole("admin", async (req, res) => {
  const tasksAvailabilityRes = await fetch(`${process.env.FASTAPI_URL}/api/v1/tasks/availability`, {
    method: "POST",
    headers: {
      "X-API-Key": process.env.FASTAPI_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: "__dummy_user__",
      display_name: "Dummy User",
      auth_method: "local",
    }),
  });
  const tasksAvailability = await tasksAvailabilityRes.json();

  res.status(tasksAvailabilityRes.status).json(tasksAvailability);
});

export default handler;
