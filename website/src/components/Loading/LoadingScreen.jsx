import { Box, Center, Progress, Text, useColorModeValue } from "@chakra-ui/react";

export const LoadingScreen = ({ text = "Loading..." } = {}) => {
  const mainBgClasses = useColorModeValue("bg-slate-300 text-gray-900", "bg-slate-900 text-white");

  return (
    <Box width="full" className={mainBgClasses}>
      <Progress size="sm" isIndeterminate />
      {text && (
        <Center width="full" className="p-12">
          <Text fontFamily="Inter">{text}</Text>
        </Center>
      )}
    </Box>
  );
};
