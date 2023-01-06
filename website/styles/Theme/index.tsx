import {
  type ThemeConfig,
  extendTheme,
  usePrefersReducedMotion,
} from "@chakra-ui/react";
import { containerTheme } from "./Components/Container";
import { StyleFunctionProps, Styles } from "@chakra-ui/theme-tools";

const config: ThemeConfig = {
  initialColorMode: "system",
  useSystemColorMode: false,
  disableTransitionOnChange: true,
};

const components = {
  Container: containerTheme,
  Box: (props: StyleFunctionProps) => ({
    backgroundColor: props.colorMode === "light" ? "white" : "gray.800",
  }),
  Button: {
    baseStyle: {
      fontWeight: "normal",
    },
    sizes: {
      lg: {
        fontSize: "md",
        paddingY: "7",
      },
    },
    variants: {
      solid: (props: StyleFunctionProps) => ({
        bg: props.colorMode === "light" ? "gray.100" : "gray.600",
        _hover: {
          bg: props.colorMode === "light" ? "gray.200" : "#3D4A60",
        },
        _active: {
          bg: props.colorMode === "light" ? "gray.300" : "#374254",
        },
        borderRadius: "lg",
      }),
      // gradient: (props: StyleFunctionProps) => ({
      //   bg: `linear-gradient(${white}, ${bgColor}) padding-box,
      //   linear-gradient(135deg, ${lgFrom}, ${lgTo}) border-box`,
      // }),
    },
  },
};

const breakpoints = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

const styles = {
  global: (props) => ({
    main: {
      fontFamily: "Inter",
    },
    header: {
      fontFamily: "Inter",
    },
  }),
};

export const theme = extendTheme({ config, styles, components, breakpoints });
