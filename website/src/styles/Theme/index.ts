import { type ThemeConfig, extendTheme } from "@chakra-ui/react";
import { Styles } from "@chakra-ui/theme-tools";

import { colors } from "./colors";
import { badgeTheme } from "./components/Badge";
import { cardTheme } from "./components/Card";
import { containerTheme } from "./components/Container";
import { tableTheme } from "./components/Table";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: true,
  disableTransitionOnChange: false,
};

const components = {
  Badge: badgeTheme,
  Container: containerTheme,
  Card: cardTheme,
  Table: tableTheme,
};

const breakpoints = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

const fonts = {
  heading: "Inter",
  body: "Inter",
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
    body: {
      position: "relative",
    },
  }),
};

export const theme = extendTheme({ colors, config, fonts, styles, components, breakpoints });
