import { defineStyleConfig } from "@chakra-ui/react";

export const badgeTheme = defineStyleConfig({
  baseStyle: {
    borderRadius: "lg",
    px: 2,
    py: 0.5,
    fontWeight: "600",
  },
  defaultProps: {
    variant: "solid",
    colorScheme: "blue",
  },
});
