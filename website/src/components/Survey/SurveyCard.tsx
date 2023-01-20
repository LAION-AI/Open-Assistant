import { Box, BoxProps, useColorModeValue } from "@chakra-ui/react";
import clsx from "clsx";
import { PropsWithChildren } from "react";

export const SurveyCard = (props: PropsWithChildren<{ className?: string }>) => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  const BoxClasses: BoxProps = {
    gap: "2",
    borderRadius: "xl",
    shadow: "base",
    className: clsx("p-4 sm:p-6", props.className),
  };

  return (
    <Box as="section" bg={backgroundColor} {...BoxClasses}>
      {props.children}
    </Box>
  );
};
