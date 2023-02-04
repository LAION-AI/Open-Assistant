import { Button, useColorMode } from "@chakra-ui/react";
import { Sun } from "lucide-react";

const ColorModeToggler = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Button size="md" width="70px" justifyContent="center" onClick={toggleColorMode} gap="4" variant="outline">
      <Sun size={"2em"} />
    </Button>
  );
};

export { ColorModeToggler };
