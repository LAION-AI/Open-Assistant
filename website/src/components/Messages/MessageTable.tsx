import { Stack, StackDivider } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";

export function MessageTable({ messages }) {
  return (
    <Stack divider={<StackDivider />} spacing="4">
      {messages.map((item) => (
        <MessageTableEntry item={item} key={item.message_id || item.id} />
      ))}
    </Stack>
  );
}
