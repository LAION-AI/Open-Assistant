import { Button, useColorMode } from "@chakra-ui/react";
import { Moon, Sun } from "lucide-react";

const ColorModeToggler = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Button size="md" p="0px" justifyContent="center" onClick={toggleColorMode} gap="4" variant="ghost">
      {colorMode === "dark" ? <Moon size={"1.5em"} /> : <Sun size={"1.5em"} />}
    </Button>
  );
};

export { ColorModeToggler };
