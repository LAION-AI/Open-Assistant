import { defineStyleConfig } from "@chakra-ui/styled-system";

const baseStyle = {};

const variants = {
  "no-padding": {
    padding: 0,
  },
};

export const containerTheme = defineStyleConfig({
  baseStyle,
  variants,
});
