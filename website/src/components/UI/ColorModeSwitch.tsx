import { Switch, useColorMode } from "@chakra-ui/react";
import React from "react";

const ColorModeSwitch = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <Switch
      onChange={toggleColorMode}
      defaultChecked={colorMode === "light"}
      checked={colorMode === "light"}
      size="lg"
    />
  );
};

export default ColorModeSwitch;