import { ChakraProvider } from "@chakra-ui/react";
import { theme } from "./Theme";

export function Chakra({ cookies, children }) {
  const cookieColorValue = cookies['chakra-ui-color-mode'] ?? "light";
  const cookieColorModeManager = {
    "type": "cookie",
    "ssr": true,
    "get": () => { return cookieColorValue },
    "set": () => { console.log("Current colorMode set to :", cookieColorValue) }
  } as const;

  return (
    <ChakraProvider theme={theme} colorModeManager={cookieColorModeManager} resetCSS>
      {children}
    </ChakraProvider>
  );
}

