import { Box, Center, Progress, Text } from "@chakra-ui/react";

export const LoadingScreen = ({ text = "Loading..." } = {}) => {
  return (
    <Box width="full">
      <Progress size="sm" isIndeterminate />
      {text && (
        <Center width="full" p="12">
          <Text>{text}</Text>
        </Center>
      )}
    </Box>
  );
};
