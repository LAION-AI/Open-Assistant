import { defineStyleConfig } from "@chakra-ui/styled-system";

export const textTheme = defineStyleConfig({
  variants: {
    h1: {
      as: "h1",
      fontSize: "2xl",
      fontWeight: "bold",
    },
  },
});
