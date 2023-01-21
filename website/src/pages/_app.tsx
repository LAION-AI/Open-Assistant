import "../styles/globals.css";
import "focus-visible";

import type { AppProps } from "next/app";
import { SessionProvider } from "next-auth/react";
import { appWithTranslation } from "next-i18next";
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

  return (
    <FlagsProvider value={flags}>
      <Chakra cookies={cookies}>
        <SWRConfig value={swrConfig}>
          <SessionProvider session={session}>{page}</SessionProvider>
        </SWRConfig>
      </Chakra>
    </FlagsProvider>
  );
}
export { getServerSideProps };
export default appWithTranslation(MyApp, nextI18NextConfig);
