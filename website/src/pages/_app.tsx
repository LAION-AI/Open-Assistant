import { SessionProvider } from "next-auth/react";

import "../styles/globals.css";
import "focus-visible";

function MyApp({ Component, pageProps: { session, ...pageProps } }) {
  return (
    <SessionProvider session={session}>
      <Component {...pageProps} />
    </SessionProvider>
  );
}

export default MyApp;
