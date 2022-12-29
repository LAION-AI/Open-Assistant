import { Button, useColorMode } from "@chakra-ui/react";
import React from "react";

type Props = {};

const ColorModeSwitch = (props: Props) => {
  const { colorMode, toggleColorMode } = useColorMode();
  return <Button onClick={toggleColorMode}>Toggle {colorMode === "light" ? "Dark" : "Light"}</Button>;
};

export default ColorModeSwitch;
