declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: "development" | "production";
      NEXT_PUBLIC_CLOUDFARE_CAPTCHA_SITE_KEY: string;
    }
  }
}
