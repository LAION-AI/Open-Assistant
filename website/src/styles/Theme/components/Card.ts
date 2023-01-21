import { cardAnatomy } from "@chakra-ui/anatomy";
import { createMultiStyleConfigHelpers } from "@chakra-ui/react";

const { definePartsStyle, defineMultiStyleConfig } = createMultiStyleConfigHelpers(cardAnatomy.keys);

export const cardTheme = defineMultiStyleConfig({
  baseStyle: definePartsStyle(({ colorMode }) => {
    const isLightMode = colorMode === "light";
    return {
      container: {
        backgroundColor: isLightMode ? "white" : "gray.700",
        p: "0",
      },
      header: {
        p: "6",
      },
      body: {
        p: "6",
      },
      footer: {
        p: "6",
      },
    };
  }),
  variants: {
    elevated: definePartsStyle({
      container: {
        borderRadius: "xl",
      },
    }),
    task: definePartsStyle({
      container: {
        borderRadius: "xl",
        borderBottomRadius: "none",
      },
    }),
  },
});
