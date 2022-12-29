import {
  extendTheme,
  type ThemeConfig,
  ChakraProvider,
  cookieStorageManagerSSR,
  localStorageManager,
} from "@chakra-ui/react";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: true,
  disableTransitionOnChange: false,
};

const styles = {
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
const theme = extendTheme({ config, styles });


export function Chakra({ cookies, children }) {
  const colorModeManager = typeof cookies === "string" ? cookieStorageManagerSSR(cookies) : localStorageManager;

  return <ChakraProvider theme={theme} colorModeManager={colorModeManager}>{children}</ChakraProvider>;
}

// also export a reusable function getServerSideProps
export function getServerSideProps({ req }) {
  return {
    props: {
      // first time users will not have any cookies and you may not return
      // undefined here, hence ?? is necessary
      cookies: req.headers.cookie ?? "",
    },
  };
}

export default theme;
