import { boolean } from "boolean";
import type { NextApiRequest, NextApiResponse } from "next";
import { BrowserConfig } from "src/types/Config";

// don't put sensitive information here
const config: BrowserConfig = {
  BYE: boolean(process.env.BYE),
  ENABLE_CHAT: boolean(process.env.ENABLE_CHAT),
  ENABLE_DRAFTS_WITH_PLUGINS: boolean(process.env.ENABLE_DRAFTS_WITH_PLUGINS),
  NUM_GENERATED_DRAFTS: Number(process.env.NUM_GENERATED_DRAFTS),
  ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
  ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
  CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
  CURRENT_ANNOUNCEMENT: process.env.CURRENT_ANNOUNCEMENT,
};

// don't check for auth
const handler = (req: NextApiRequest, res: NextApiResponse) => {
  return res.status(200).json(config);
};

export default handler;
