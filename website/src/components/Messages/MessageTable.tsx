import { Box, CircularProgress, Stack, StackDivider, useColorModeValue } from "@chakra-ui/react";
import { MessageTableEntry } from "./MessageTableEntry";

export function MessageTable({ messages, isLoading }) {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const accentColor = useColorModeValue("gray.200", "gray.900");

  return (
    <Box
      backgroundColor={backgroundColor}
      boxShadow="base"
      dropShadow={accentColor}
      borderRadius="xl"
      className="p-6 shadow-sm"
    >
      {isLoading ? (
        <CircularProgress isIndeterminate />
      ) : (
        <Stack divider={<StackDivider />} spacing="4">
          {messages.map((item, idx) => (
            <MessageTableEntry item={item} idx={idx} key={item.id} />
          ))}
        </Stack>
      )}
    </Box>
  );
}
