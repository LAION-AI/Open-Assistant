import { createContext, useContext } from "react";

export interface BrowserConfig {
  ENABLE_CHAT: boolean;
  ENABLE_EMAIL_SIGNIN: boolean;
  ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean;
  CLOUDFLARE_CAPTCHA_SITE_KEY: string;
  CURRENT_ANNOUNCEMENT: string;
}

export const BrowserConfigContext = createContext<BrowserConfig>({} as any);

export const useBrowserConfig = () => useContext(BrowserConfigContext);
