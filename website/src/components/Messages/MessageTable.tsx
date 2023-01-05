import { Box, CircularProgress, Stack, StackDivider, useColorModeValue } from "@chakra-ui/react";
import { MessageTableEntry } from "./MessageTableEntry";

export function MessageTable({ messages }) {
  return (
    <Stack divider={<StackDivider />} spacing="4">
      {messages.map((item, idx) => (
        <MessageTableEntry item={item} idx={idx} key={item.id} />
      ))}
    </Stack>
  );
}
