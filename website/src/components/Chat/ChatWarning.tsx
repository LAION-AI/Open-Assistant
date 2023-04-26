import { Box } from "@chakra-ui/react";

export const ChatWarning = () => {
  return (
    <Box fontSize="sm" textAlign="center" mb="2" className="max-w-5xl mx-auto">
      This Assistant is a demonstration version that does not have internet access. It may generate incorrect or
      misleading information. It is not suitable for important use cases or for giving advice.
    </Box>
  );
};
