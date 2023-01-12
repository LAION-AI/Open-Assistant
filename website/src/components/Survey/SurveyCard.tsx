import { Box, BoxProps, useColorModeValue } from "@chakra-ui/react";

interface SurveyCardProps {
  className?: string;
  children: React.ReactNode;
}

export const SurveyCard = (props: SurveyCardProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  const BoxClasses: BoxProps = {
    p: "6",
    gap: "2",
    borderRadius: "xl",
    shadow: "base",
  };

  return (
    <Box bg={backgroundColor} {...BoxClasses}>
      {props.children}
    </Box>
  );
};
