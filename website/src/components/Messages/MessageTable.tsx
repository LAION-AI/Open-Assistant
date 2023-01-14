import { Stack } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { Message } from "src/types/Conversation";

interface MessageTableProps {
  messages: Message[];
  enableLink?: boolean;
}

export function MessageTable({ messages, enableLink }: MessageTableProps) {
  return (
    <Stack spacing="3">
      {messages.map((item) => (
        <MessageTableEntry enabled={enableLink} item={item} key={item.id || item.frontend_message_id} />
      ))}
    </Stack>
  );
}
