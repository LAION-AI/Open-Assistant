declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: "development" | "production";
      NEXT_PUBLIC_CLOUDFLARE_CAPTCHA_SITE_KEY: string;
      CLOUDFLARE_CAPTCHA_SERCERT_KEY: string;
    }
  }
}

export {};
