import { Box, Progress, Text } from "@chakra-ui/react";

export const LoadingScreen = ({ text = "Loading..." } = {}) => {
  return (
    <Box width="full">
      <Progress size="sm" isIndeterminate />
      {text && (
        <Box width="full">
          <Text fontFamily="Inter">{text}</Text>
        </Box>
      )}
    </Box>
  );
};
