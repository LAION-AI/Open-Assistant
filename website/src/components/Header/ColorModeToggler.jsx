import { Button, useColorMode } from "@chakra-ui/react";
import { Sun, Moon } from "lucide-react";
import { useEffect } from "react";
import { useCookies } from "react-cookie";

const ColorModeToggler = () => {
  const [cookies, setCookie] = useCookies(["chakra-ui-color-mode"]);
  const { colorMode, toggleColorMode } = useColorMode();
  
  useEffect(() => {
    setCookie("chakra-ui-color-mode", colorMode, { path: "/" });
  }, [toggleColorMode, colorMode]);
  
  return (
    <Button size="md" p="0px" justifyContent="center" onClick={toggleColorMode} gap="4" variant="ghost">
      {colorMode == "dark" ? <Sun size={"1.5em"} /> : <Moon size={"1.5em"} />}
    </Button>
  );
};

export { ColorModeToggler };