import { extendTheme, type ThemeConfig } from "@chakra-ui/react";
import { containerTheme } from "./components/Container";
import { Styles, mode } from "@chakra-ui/theme-tools";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: true,
  disableTransitionOnChange: false,
};

const components = {
  Container: containerTheme,
};

const styles: Styles = {
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
};

export const theme = extendTheme({ config, styles, components });
