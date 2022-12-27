import { ChakraProvider } from "@chakra-ui/react";
import { SessionProvider } from "next-auth/react";
import { Inter } from "@next/font/google";
import { extendTheme } from "@chakra-ui/react";

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

function MyApp({ Component, pageProps: { session, ...pageProps } }) {
  return (
    <ChakraProvider theme={theme}>
      <SessionProvider session={pageProps.session}>
        <Component {...pageProps} />
      </SessionProvider>
    </ChakraProvider>
  );
}

export default MyApp;
