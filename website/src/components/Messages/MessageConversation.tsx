import { Stack } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { Message } from "src/types/Conversation";

interface MessageConversationProps {
  messages: Message[];
  enableLink?: boolean;
  highlightLastMessage?: boolean;
}

export function MessageConversation({ messages, enableLink, highlightLastMessage }: MessageConversationProps) {
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
