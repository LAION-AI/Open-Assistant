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
import { DefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { BrowserEnvContext } from "src/hooks/env/BrowserEnv";
import { get } from "src/lib/api";
import { BrowserEnv } from "src/lib/browserEnv";
import { BrowserConfig } from "src/types/Config";
import { SWRConfig, SWRConfiguration } from "swr";
import useSWRImmutable from "swr/immutable"

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

  const { data } = useSWRImmutable<BrowserConfig>("/api/config", get);

  const Layout = Component.getLayout ?? DefaultLayout;
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
              <BrowserEnvContext.Provider value={(data ?? {}) as any}>
                <Layout>
                  <Component {...pageProps} />
                </Layout>
              </BrowserEnvContext.Provider>
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
