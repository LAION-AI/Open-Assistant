import { ColorModeScript } from "@chakra-ui/react";
import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html className="h-full antialiased" lang="en">
      <Head>
        <link rel="shortcut icon" type="image/png" href="/images/logos/favicon.png" />
      </Head>
      <body className="flex h-full flex-col bg-gray-50">
        <ColorModeScript type='localStorage' />
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
