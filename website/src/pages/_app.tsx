import "../styles/globals.css";
import "focus-visible";

import { ChakraProvider } from "@chakra-ui/react";
import { extendTheme } from "@chakra-ui/react";
import { Inter } from "@next/font/google";
import type { AppProps } from "next/app";
import { SessionProvider } from "next-auth/react";
import { getDefaultLayout, NextPageWithLayout } from "src/components/Layout";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const theme = extendTheme({
  styles: {
    global: {
      body: {
        bg: "white",
      },
      main: {
        fontFamily: "Inter",
      },
      header: {
        fontFamily: "Inter",
      },
    },
  },
});

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

function MyApp({ Component, pageProps: { session, ...pageProps } }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? getDefaultLayout;
  const page = getLayout(<Component {...pageProps} />);

  return (
    <ChakraProvider theme={theme}>
      <SessionProvider session={session}>{page}</SessionProvider>
    </ChakraProvider>
  );
}

export default MyApp;
