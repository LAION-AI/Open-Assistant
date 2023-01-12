import { Stack, StackDivider } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { Message } from "src/types/Conversation";

interface MessageTableProps {
  messages: Message[];
}

export function MessageTable({ messages }: MessageTableProps) {
  return (
    <Stack divider={<StackDivider />} spacing="4">
      {messages.map((item) => (
        <MessageTableEntry item={item} key={item.id || item.frontend_message_id} />
      ))}
    </Stack>
  );
}
