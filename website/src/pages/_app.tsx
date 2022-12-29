import { SessionProvider } from "next-auth/react";
import type { AppProps } from "next/app";

import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";

import "../styles/globals.css";
import "focus-visible";
import { Chakra, getServerSideProps } from "../styles/Theme";

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

function MyApp({ Component, pageProps: { session, cookies, ...pageProps } }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? getDefaultLayout;
  const page = getLayout(<Component {...pageProps} />);

  return (
    <Chakra cookies={cookies}>
      <SessionProvider session={session}>{page}</SessionProvider>
    </Chakra>
  );
}
export { getServerSideProps };
export default MyApp;
