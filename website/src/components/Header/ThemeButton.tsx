import { IconButton, Tooltip, useColorMode } from "@chakra-ui/react";
import { Moon, Sun } from "lucide-react";

export function ThemeButton() {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Tooltip fontFamily="inter" label="Toggle Dark Mode" placement="right" className="hidden lg:hidden sm:block">
      <IconButton
        aria-label="Toggle Dark Mode"
        size="md"
        onClick={toggleColorMode}
        variant="outline"
        icon={colorMode === "light" ? <Sun size={"1em"} /> : <Moon size={"1em"} />}
      />
    </Tooltip>
  );
}
