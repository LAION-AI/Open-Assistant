import { createContext, useContext } from "react";

export interface BrowserEnv {
  ENABLE_CHAT: boolean;
  ENABLE_EMAIL_SIGNIN: boolean;
  ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean;
  CLOUDFLARE_CAPTCHA_SITE_KEY: string;
}

export const BrowserEnvContext = createContext<BrowserEnv>({} as any);

export const useBrowserEnv = () => useContext(BrowserEnvContext);
