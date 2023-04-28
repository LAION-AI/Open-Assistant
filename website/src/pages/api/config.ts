import { boolean } from "boolean";
import { withoutRole } from "src/lib/auth";
import { BrowserConfig } from "src/types/Config";

const config: BrowserConfig = {
  ENABLE_CHAT: boolean(process.env.ENABLE_CHAT),
  ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
  ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
  CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
  CURRENT_ANNOUNCEMENT: process.env.CURRENT_ANNOUNCEMENT,
};

const handler = withoutRole("banned", async (req, res, token) => {
  return res.status(200).json(config);
});

export default handler;
