declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: "development" | "production";
      NEXT_PUBLIC_CLOUDFLARE_CAPTCHA_SITE_KEY: string;
      CLOUDFLARE_CAPTCHA_SECRET_KEY: string;
      NEXT_PUBLIC_ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean;
      NEXT_PUBLIC_ENABLE_EMAIL_SIGNIN: boolean;
      ADMIN_USERS: string;
      MODERATOR_USERS: string;
    }
  }
}

export {};
