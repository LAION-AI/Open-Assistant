import type { NextApiRequest, NextApiResponse } from "next";
import { getToken, JWT } from "next-auth/jwt";

/**
 * Wraps any API Route handler and verifies that the user does not have the
 * specified role.  Returns a 403 if they do, otherwise runs the handler.
 */
const withoutRole = (role: string, handler: (arg0: NextApiRequest, arg1: NextApiResponse, arg2: JWT) => void) => {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = await getToken({ req });
    if (!token || token.role === role) {
      res.status(403).end();
      return;
    }
    return handler(req, res, token);
  };
};

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

export { withoutRole, withRole };
