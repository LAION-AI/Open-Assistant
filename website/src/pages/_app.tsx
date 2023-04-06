import "../styles/globals.css";
import "focus-visible";

import { boolean } from "boolean";
import type { AppContext, AppProps } from "next/app";
import Head from "next/head";
import { SessionProvider } from "next-auth/react";
import { appWithTranslation, useTranslation } from "next-i18next";
import React, { useEffect } from "react";
import { FlagsProvider } from "react-feature-flags";
import { DefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { BrowserEnv, BrowserEnvContext } from "src/hooks/env/useBrowserEnv";
import { SWRConfig, SWRConfiguration } from "swr";

import nextI18NextConfig from "../../next-i18next.config.js";
import { Chakra } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
  env: BrowserEnv;
  cookie: string;
};

const swrConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnMount: true,
};

function MyApp({ Component, pageProps: { session, ...pageProps }, env, cookie }: AppPropsWithLayout) {
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
              <BrowserEnvContext.Provider value={env}>
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

MyApp.getInitialProps = ({ ctx: { req } }: AppContext) => {
  const env: BrowserEnv = {
    ENABLE_CHAT: boolean(process.env.ENABLE_CHAT),
    ENABLE_EMAIL_SIGNIN: boolean(process.env.ENABLE_EMAIL_SIGNIN),
    ENABLE_EMAIL_SIGNIN_CAPTCHA: boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA),
    CLOUDFLARE_CAPTCHA_SITE_KEY: process.env.CLOUDFLARE_CAPTCHA_SITE_KEY,
  };

  return {
    env,
    cookie: req?.headers.cookie,
  };
};

export default appWithTranslation(MyApp, nextI18NextConfig);
