import { ChakraProvider, cookieStorageManagerSSR, localStorageManager } from "@chakra-ui/react";
import { PropsWithChildren } from "react";

import { theme } from "./Theme";

export function Chakra({ cookie, children }: PropsWithChildren<{ cookie?: string }>) {
  const colorModeManager = typeof cookie === "string" ? cookieStorageManagerSSR(cookie) : localStorageManager;

  return (
    <ChakraProvider theme={theme} colorModeManager={colorModeManager} resetCSS>
      {children}
    </ChakraProvider>
  );
}
