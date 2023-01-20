import { Box, BoxProps, useColorModeValue } from "@chakra-ui/react";
import { PropsWithChildren } from "react";

export const SurveyCard = (props: PropsWithChildren<{ className?: string }>) => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  const BoxClasses: BoxProps = {
    gap: "2",
    borderRadius: "xl",
    shadow: "base",
    className: "p-4 sm:p-6 " + (props.className ?? ""),
  };

  return (
    <Box as="section" bg={backgroundColor} {...BoxClasses}>
      {props.children}
    </Box>
  );
};
