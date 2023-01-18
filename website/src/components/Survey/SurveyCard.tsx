import { Box, BoxProps, useColorModeValue } from "@chakra-ui/react";

interface SurveyCardProps {
  className?: string;
  children: React.ReactNode;
}

export const SurveyCard = (props: SurveyCardProps) => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  const BoxClasses: BoxProps = {
    gap: "2",
    borderRadius: "xl",
    shadow: "base",
    className: "p-4 sm:p-6",
  };

  return (
    <Box bg={backgroundColor} {...BoxClasses}>
      {props.children}
    </Box>
  );
};
