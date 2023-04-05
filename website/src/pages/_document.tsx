import { boolean } from "boolean";
import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html className="h-full antialiased" lang="en">
      <Head>
        <link rel="shortcut icon" type="image/png" href="/images/logos/favicon.png" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
            var process = {
              env: new Proxy(${JSON.stringify(getEnviromentVariables())}, {
                get(env, key) {
                  if (!(key in env)) {
                    console.warn(\`Environment variable \${key} not set in _document.tsx\`);
                  }
                  return env[key];
                },
              })
            }
            `,
          }}
        ></script>
      </Head>
      <body className="flex h-full flex-col">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

const getEnviromentVariables = () => {
  return {
    INFERENCE_SERVER_HOST: process.env.INFERENCE_SERVER_HOST,
    ENABLE_CHAT: boolean(process.env.ENABLE_CHAT),
    ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
    ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
    CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
    NODE_ENV: process.env.NODE_ENV,
  };
};
