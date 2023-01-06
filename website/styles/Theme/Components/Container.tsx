import {
  color,
  defineStyle,
  defineStyleConfig,
  // transition,
} from "@chakra-ui/styled-system";
import { colors } from "../colors";

const baseStyle = defineStyle(({ colorMode }) => ({
  minWidth: "100%",
  bg: colorMode === "light" ? colors.light.bg : colors.dark.bg,
  // transition: "background-color 300ms cubic-bezier(0.4, 0, 1, 1)",
  color: colorMode === "light" ? colors.light.text : colors.dark.text,
}));

const variants = {
  "no-padding": {
    padding: 0,
  },
};

export const containerTheme = defineStyleConfig({
  baseStyle,
  variants,
});
