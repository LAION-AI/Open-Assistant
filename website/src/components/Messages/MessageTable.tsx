import { Stack } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { Message } from "src/types/Conversation";

interface MessageTableProps {
  messages: Message[];
  enableLink?: boolean;
  highlightLastMessage?: boolean;
}

export function MessageTable({ messages, enableLink, highlightLastMessage }: MessageTableProps) {
  return (
    <Stack spacing="4">
      {messages.map((message, idx) => (
        <MessageTableEntry
          enabled={enableLink}
          message={message}
          key={message.id + message.frontend_message_id}
          highlight={highlightLastMessage && idx === messages.length - 1}
        />
      ))}
    </Stack>
  );
}
