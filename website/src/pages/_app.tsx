import "../styles/globals.css";
import "focus-visible";

import { boolean } from "boolean";
import type { AppContext, AppProps } from "next/app";
import Head from "next/head";
import { SessionProvider } from "next-auth/react";
import { appWithTranslation, useTranslation } from "next-i18next";
import React, { useEffect } from "react";
import { FlagsProvider } from "react-feature-flags";
import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { isChatEnabled } from "src/lib/chat_enabled";
import { SWRConfig, SWRConfiguration } from "swr";

import nextI18NextConfig from "../../next-i18next.config.js";
import { Chakra } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
  env: typeof process.env;
  cookie: string;
};

const swrConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnMount: true,
};

function MyApp({ Component, pageProps: { session, ...pageProps }, env, cookie }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? getDefaultLayout;
  const page = getLayout(<Component {...pageProps} />);
  const { t, i18n } = useTranslation();

  const direction = i18n.dir();
  useEffect(() => {
    document.body.dir = direction;
  }, [direction]);

  // expose env vars on the client
  if (typeof window !== "undefined") {
    process.env = new Proxy(env, {
      get(env, key: string) {
        if (!(key in env)) {
          console.warn(`Environment variable ${key} not set in _app.tsx`);
        }
        return env[key];
      },
    });
  }

  return (
    <>
      <Head>
        <meta name="description" key="description" content={t("index:description")} />
      </Head>
      <FlagsProvider value={flags}>
        <Chakra cookie={cookie}>
          <SWRConfig value={swrConfig}>
            <SessionProvider session={session}>{page}</SessionProvider>
          </SWRConfig>
        </Chakra>
      </FlagsProvider>
    </>
  );
}

MyApp.getInitialProps = ({ ctx: { req } }: AppContext) => {
  return {
    env: {
      INFERENCE_SERVER_HOST: process.env.INFERENCE_SERVER_HOST,
      ENABLE_CHAT: isChatEnabled(),
      ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
      ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
      CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
      NODE_ENV: process.env.NODE_ENV,
    },
    cookie: req?.headers.cookie,
  };
};

export default appWithTranslation(MyApp, nextI18NextConfig);
