import "../styles/globals.css";
import "focus-visible";

import type { AppProps } from "next/app";
import { SessionProvider } from "next-auth/react";
import { FlagsProvider } from "react-feature-flags";
import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";
import flags from "src/flags";

import { Chakra, getServerSideProps } from "../styles/Chakra";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

function MyApp({ Component, pageProps: { session, cookies, ...pageProps } }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? getDefaultLayout;
  const page = getLayout(<Component {...pageProps} />);

  return (
    <FlagsProvider value={flags}>
      <Chakra cookies={cookies}>
        <SessionProvider session={session}>{page}</SessionProvider>
      </Chakra>
    </FlagsProvider>
  );
}
export { getServerSideProps };
export default MyApp;
