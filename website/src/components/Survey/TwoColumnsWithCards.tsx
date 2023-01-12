import { Box, Stack } from "@chakra-ui/react";
import { SurveyCard } from "src/components/Survey/SurveyCard";

export const TwoColumnsWithCards = ({ children }: { children: React.ReactNode[] }) => {
  if (!Array.isArray(children) || children.length !== 2) {
    throw new Error("TwoColumns expects 2 children");
  }

  const [first, second] = children;

  return (
    <Box mb="4">
      <Stack spacing="4">
        <SurveyCard>{first}</SurveyCard>
        <SurveyCard>{second}</SurveyCard>
      </Stack>
    </Box>
  );
};
