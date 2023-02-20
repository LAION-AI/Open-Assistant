import "../styles/globals.css";
import "focus-visible";

import type { AppProps } from "next/app";
import Head from "next/head";
import { SessionProvider } from "next-auth/react";
import { appWithTranslation, useTranslation } from "next-i18next";
import React, { useEffect } from "react";
import { FlagsProvider } from "react-feature-flags";
import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";
import { SWRConfig, SWRConfiguration } from "swr";

import nextI18NextConfig from "../../next-i18next.config.js";
import { Chakra, getServerSideProps } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const swrConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnMount: true,
};

function MyApp({ Component, pageProps: { session, cookies, ...pageProps } }: AppPropsWithLayout) {
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
        <Chakra cookies={cookies}>
          <SWRConfig value={swrConfig}>
            <SessionProvider session={session}>{page}</SessionProvider>
          </SWRConfig>
        </Chakra>
      </FlagsProvider>
    </>
  );
}
export { getServerSideProps };
export default appWithTranslation(MyApp, nextI18NextConfig);
