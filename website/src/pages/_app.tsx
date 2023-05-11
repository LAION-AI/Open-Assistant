import "../styles/globals.css";
import "focus-visible";

import type { AppContext, AppProps } from "next/app";
import App from "next/app";
import Head from "next/head";
import { SessionProvider } from "next-auth/react";
import { appWithTranslation, useTranslation } from "next-i18next";
import React, { useEffect } from "react";
import { FlagsProvider } from "react-feature-flags";
import { DefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { BrowserConfigContext } from "src/hooks/env/BrowserEnv";
import { get } from "src/lib/api";
import { BrowserConfig } from "src/types/Config";
import { SWRConfig, SWRConfiguration } from "swr";
import useSWRImmutable from "swr/immutable";

import nextI18NextConfig from "../../next-i18next.config.js";
import { Chakra } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const swrConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnMount: true,
};

function MyApp({ Component, pageProps: { session, ...pageProps } }: AppPropsWithLayout) {
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
        <Chakra>
          <SWRConfig value={swrConfig}>
            <SessionProvider session={session}>
              <BrowserConfigContext.Provider value={(data ?? {}) as any}>
                <Layout>
                  <Component {...pageProps} />
                </Layout>
              </BrowserConfigContext.Provider>
            </SessionProvider>
          </SWRConfig>
        </Chakra>
      </FlagsProvider>
    </>
  );
}

export default appWithTranslation(MyApp, nextI18NextConfig);
