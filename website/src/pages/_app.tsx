import "../styles/globals.css";
import "focus-visible";

import { boolean } from "boolean";
import { minutesToMilliseconds } from "date-fns";
import type { AppContext, AppProps } from "next/app";
import App from "next/app";
import Head from "next/head";
import { Session } from "next-auth";
import { getSession, SessionProvider } from "next-auth/react";
import { appWithTranslation, useTranslation } from "next-i18next";
import React, { useEffect } from "react";
import { FlagsProvider } from "react-feature-flags";
import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { BrowserEnvContext } from "src/hooks/env/BrowserEnv";
import { get } from "src/lib/api";
import { BrowserEnv } from "src/lib/browserEnv";
import { BrowserConfig } from "src/types/Config";
import useSWR, { SWRConfig, SWRConfiguration } from "swr";

import nextI18NextConfig from "../../next-i18next.config.js";
import { Chakra } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
} & AppInitialProps;

const swrConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnMount: true,
};

function MyApp({ Component, pageProps: { session, ...pageProps }, cookie, env }: AppPropsWithLayout) {
  // expose env vars on the client
  if (typeof window !== "undefined") {
    (window as unknown as { __env: BrowserEnv }).__env = env;
  }

  const { data } = useSWR<BrowserConfig>("/api/config", get, {
    refreshInterval: minutesToMilliseconds(15),
  });

  const getLayout = Component.getLayout ?? getDefaultLayout;
  const page = getLayout(<Component {...pageProps} />);
  const { t, i18n } = useTranslation();

  const direction = i18n.dir();
  useEffect(() => {
    document.body.dir = direction;
  }, [direction]);

  return (
    <>
      <Head>
        <meta name="description" key="description" content={t("index:description")} />
      </Head>
      <FlagsProvider value={flags}>
        <Chakra cookie={cookie}>
          <SWRConfig value={swrConfig}>
            <SessionProvider session={session}>
              <BrowserEnvContext.Provider value={(data ?? {}) as any}>{page}</BrowserEnvContext.Provider>
            </SessionProvider>
          </SWRConfig>
        </Chakra>
      </FlagsProvider>
    </>
  );
}

type AppInitialProps = { env: BrowserEnv; cookie: string; session: Session };

MyApp.getInitialProps = async (context: AppContext): Promise<AppInitialProps> => {
  const appProps = await App.getInitialProps(context);
  const session = await getSession();
  console.log(process.env.ENABLE_CHAT);
  return {
    ...appProps,
    session,
    env: {
      ENABLE_CHAT: boolean(process.env.ENABLE_CHAT),
      ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
      ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
      CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
      CURRENT_ANNOUNCEMENT: process.env.CURRENT_ANNOUNCEMENT,
      NODE_ENV: process.env.NODE_ENV,
    },
    cookie: context.ctx.req?.headers.cookie || "",
  };
};

export default appWithTranslation(MyApp, nextI18NextConfig);
