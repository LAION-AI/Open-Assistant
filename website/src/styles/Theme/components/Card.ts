import { cardAnatomy } from "@chakra-ui/anatomy";
import { createMultiStyleConfigHelpers } from "@chakra-ui/react";

const { definePartsStyle, defineMultiStyleConfig } = createMultiStyleConfigHelpers(cardAnatomy.keys);

export const cardTheme = defineMultiStyleConfig({
  baseStyle: definePartsStyle(({ colorMode }) => {
    const isLightMode = colorMode === "light";
    return {
      container: {
        backgroundColor: isLightMode ? "white" : "gray.700",
      },
      header: {},
      body: {
        padding: 6,
      },
      footer: {},
    };
  }),
  sizes: {
    md: definePartsStyle({
      container: {
        borderRadius: "xl",
      },
    }),
  },
  variants: {
    json: definePartsStyle(({ colorMode }) => {
      const isLightMode = colorMode === "light";
      return {
        container: {
          backgroundColor: isLightMode ? "gray.100" : "gray.800",
        },
      };
    }),
  },
});
