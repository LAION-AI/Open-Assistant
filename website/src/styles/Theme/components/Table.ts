import { tableAnatomy } from "@chakra-ui/anatomy";
import { createMultiStyleConfigHelpers } from "@chakra-ui/react";

const { definePartsStyle, defineMultiStyleConfig } = createMultiStyleConfigHelpers(tableAnatomy.keys);

export const tableTheme = defineMultiStyleConfig({
  variants: {
    simple: definePartsStyle(({ colorMode }) => {
      const isLightMode = colorMode === "light";
      return {
        td: {
          borderColor: isLightMode ? "gray.100" : "gray.800",
        },
        th: {
          borderColor: isLightMode ? "gray.100" : "gray.800",
        },
      };
    }),
  },
});
