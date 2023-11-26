export interface BrowserConfig {
  BYE: boolean;
  ENABLE_CHAT: boolean;
  ENABLE_DRAFTS_WITH_PLUGINS: boolean; // Whether draft messages should be generated if plugins are in use
  NUM_GENERATED_DRAFTS: number;
  ENABLE_EMAIL_SIGNIN: boolean;
  ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean;
  CLOUDFLARE_CAPTCHA_SITE_KEY: string;
  CURRENT_ANNOUNCEMENT: string;
}
