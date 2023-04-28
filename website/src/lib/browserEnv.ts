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
    const x = (window as unknown as { __env: BrowserEnv }).__env || ({} as BrowserEnv);
    // console.log(x);
    return x;
  }
  return process.env;
};
