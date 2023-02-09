import { Box, BoxProps, useColorModeValue } from "@chakra-ui/react";
import clsx from "clsx";
import { useMemo } from "react";

export const SurveyCard = (props: BoxProps) => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  const boxProps: BoxProps = useMemo(
    () => ({
      gap: "2",
      borderRadius: "xl",
      shadow: "base",
      ...props,
      className: clsx("p-4 sm:p-6", props.className),
    }),
    [props]
  );

  return (
    <Box as="section" bg={backgroundColor} {...boxProps}>
      {props.children}
    </Box>
  );
};
