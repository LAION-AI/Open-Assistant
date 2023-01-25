import { NextApiRequest, NextApiResponse } from "next";

export default function handler(_: NextApiRequest, res: NextApiResponse) {
  return res.status(200).json({
    url: "/auth/signin?error=InvalidCaptcha",
  });
}
