import { Stack, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { Message } from "src/types/Conversation";

interface MessageConversationProps {
  messages: Message[];
  enableLink?: boolean;
  highlightLastMessage?: boolean;
}

export function MessageConversation({ messages, enableLink, highlightLastMessage }: MessageConversationProps) {
  const { t } = useTranslation("message");
  return (
    <Stack spacing="4">
      {messages.length === 0 ? (
        <Text>{t("no_messages")}</Text>
      ) : (
        messages.map((message, idx) => (
          <MessageTableEntry
            enabled={enableLink}
            message={message}
            key={message.id + message.frontend_message_id}
            highlight={highlightLastMessage && idx === messages.length - 1}
          />
        ))
      )}
    </Stack>
  );
}
