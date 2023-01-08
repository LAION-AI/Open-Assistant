import type { NextApiRequest, NextApiResponse } from "next";
import { getToken } from "next-auth/jwt";

/**
 * Wraps any API Route handler and verifies that the user has the appropriate
 * role before running the handler.  Returns a 403 otherwise.
 */
const withRole = (role: string, handler: (arg0: NextApiRequest, arg1: NextApiResponse) => void) => {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = await getToken({ req });
    if (!token || token.role !== role) {
      res.status(403).end();
      return;
    }
    return handler(req, res);
  };
};

export default withRole;
