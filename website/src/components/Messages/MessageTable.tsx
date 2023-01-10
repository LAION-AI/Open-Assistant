import { Stack, StackDivider } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";

export function MessageTable({ messages, valid_labels }) {
  return (
    <Stack divider={<StackDivider />} spacing="4">
      {messages.map((item, idx) => (
        <MessageTableEntry item={item} idx={idx} key={item.message_id || item.id} valid_labels={valid_labels} />
      ))}
    </Stack>
  );
}
