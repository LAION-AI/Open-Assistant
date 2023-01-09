import { type ThemeConfig, extendTheme } from "@chakra-ui/react";
import { Styles } from "@chakra-ui/theme-tools";

import { colors } from "./colors";
import { containerTheme } from "./components/Container";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: true,
  disableTransitionOnChange: false,
};

const components = {
  Container: containerTheme,
};

const breakpoints = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

const styles: Styles = {
  global: (props) => ({
    "*": {
      transition: "background-color 200ms cubic-bezier(0.4, 0, 1, 1)",
      // bg: props.colorMode === "light" ? colors.light.bg : colors.dark.bg,
      // color: props.colorMode === "light" ? colors.light.text : colors.dark.text,
    },
    ".oa-basic-theme": {
      bg: props.colorMode === "light" ? colors.light.bg : colors.dark.bg,
      color: props.colorMode === "light" ? colors.light.text : colors.dark.text,
    },
    main: {
      fontFamily: "Inter",
    },
    header: {
      fontFamily: "Inter",
    },
  }),
};

export const theme = extendTheme({ colors, config, styles, components, breakpoints });
