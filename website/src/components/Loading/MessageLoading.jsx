import { Box, Progress, useColorModeValue } from "@chakra-ui/react";

export const MessageLoading = () => {
  const loadingColor = useColorModeValue("gray.200", "gray.600");

  return (
    <Box className="w-full">
      <Progress size="sm" isIndeterminate />
      <Box className="flex flex-col gap-2 my-8">
        <Box width="28" padding="4" borderRadius="md" bg={loadingColor}></Box>
        <Box width="full" maxWidth="xl" height="16" bg={loadingColor} padding="4" borderRadius="xl"></Box>
      </Box>
      <Box className="flex flex-col gap-2 mb-4">
        <Box width="28" padding="4" borderRadius="md" bg={loadingColor}></Box>
        <Box width="full" maxWidth="lg" height="16" bg={loadingColor} padding="4" borderRadius="xl"></Box>
      </Box>
    </Box>
  );
};
