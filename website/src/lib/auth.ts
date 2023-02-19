import type { NextApiRequest, NextApiResponse } from "next";
import { getToken, JWT } from "next-auth/jwt";
import { Role } from "src/components/RoleSelect";

/**
 * Wraps any API Route handler and verifies that the user does not have the
 * specified role.  Returns a 403 if they do, otherwise runs the handler.
 */
const withoutRole = (role: Role, handler: (arg0: NextApiRequest, arg1: NextApiResponse, arg2: JWT) => void) => {
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
const withRole = (role: Role, handler: (arg0: NextApiRequest, arg1: NextApiResponse, token: JWT) => void) => {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = await getToken({ req });
    if (!token || token.role !== role) {
      res.status(403).end();
      return;
    }
    return handler(req, res, token);
  };
};

export const withAnyRole = (
  roles: Role[],
  handler: (arg0: NextApiRequest, arg1: NextApiResponse, token: JWT) => void
) => {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = await getToken({ req });
    if (!token || roles.every((role) => token.role !== role)) {
      res.status(403).end();
      return;
    }
    return handler(req, res, token);
  };
};

export { withoutRole, withRole };
