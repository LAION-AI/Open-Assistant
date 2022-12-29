import { color, defineStyle, defineStyleConfig, transition } from "@chakra-ui/styled-system"
import { colors } from "../colors"

const baseStyle = defineStyle(({colorMode}) => ({
  minWidth: "100%",
  bg: colorMode === "light" ? colors.light.bg : colors.dark.bg,
  transition: "background-color 250ms ease-in",
  color: colorMode === "light" ? colors.light.text : colors.dark.text,
}))

export const containerTheme = defineStyleConfig({
  baseStyle,
})