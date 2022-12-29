import { ChakraProvider } from "@chakra-ui/react";
import { SessionProvider } from "next-auth/react";
import { Inter } from "@next/font/google";
import { extendTheme } from "@chakra-ui/react";
import type { AppProps } from "next/app";

import { NextPageWithLayout, getDefaultLayout } from "src/components/Layout";

import "../styles/globals.css";
import "focus-visible";

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
