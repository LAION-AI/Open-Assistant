export type BrowserEnv = Pick<
  typeof process.env,
  | "ENABLE_CHAT"
  | "ENABLE_EMAIL_SIGNIN"
  | "ENABLE_EMAIL_SIGNIN_CAPTCHA"
  | "CLOUDFLARE_CAPTCHA_SITE_KEY"
  | "NODE_ENV"
  | "CURRENT_ANNOUNCEMENT"
>;

export const getEnv = (): BrowserEnv => {
  if (typeof window !== "undefined") {
    return (window as unknown as { __env: BrowserEnv }).__env || ({} as BrowserEnv);
  }
  return process.env;
};
