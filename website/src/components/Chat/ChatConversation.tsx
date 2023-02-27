/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Flex, Textarea, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { InferenceMessage, InferenceResponse } from "src/types/Chat";
import useSWRMutation from "swr/mutation";

import { BaseMessageEntry } from "../Messages/BaseMessageEntry";
import { MessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
interface ChatConversationProps {
  chatId: string;
}

export const ChatConversation = ({ chatId }: ChatConversationProps) => {
  const { t } = useTranslation("common");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<InferenceMessage[]>([]);
  const [streamedResponse, setResponse] = useState<string | null>("");

  const isLoading = Boolean(streamedResponse);

  const send = useCallback(async () => {
    if (!inputRef.current) {
      return;
    }

    const content = inputRef.current.value.trim();

    if (!content || !chatId) {
      return;
    }

    setResponse("...");

    const parent_id = messages[messages.length - 1]?.id ?? null;
    // we have to do this manually since we want to stream the chunks
    // there is also EventSource, but it only works with get requests.
    const { body } = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, content, parent_id }),
    });

    // first chunk is message information
    const stream = iteratorSSE(body!);
    const { value } = await stream.next();
    const response: InferenceResponse = JSON.parse(value.data);

    setMessages((messages) => [...messages, response.prompter_message]);

    // remaining messages are the tokens
    let responseMessage = "";
    for await (const { data } of stream) {
      const text = JSON.parse(data).token.text;
      responseMessage += text;
      setResponse(responseMessage);
      // wait for re-render
      await new Promise(requestAnimationFrame);
    }

    setMessages((old) => [...old, { ...response.assistant_message, content: responseMessage }]);
    setResponse(null);
  }, [chatId, messages]);

  return (
    <Flex flexDir="column" gap={4} overflowY="auto">
      {messages.map((message) => (
        <ChatMessageEntry
          key={message.id}
          isAssistant={message.role === "assistant"}
          messageId={message.id}
          chatId={chatId}
          isPending={false}
        >
          {message.content}
        </ChatMessageEntry>
      ))}
      {streamedResponse ? (
        <ChatMessageEntry isAssistant chatId={chatId} isPending>
          {streamedResponse}
        </ChatMessageEntry>
      ) : (
        <Textarea ref={inputRef} autoFocus />
      )}
      <Button onClick={send} isDisabled={isLoading}>
        {t("submit")}
      </Button>
    </Flex>
  );
};

type ChatMessageEntryProps = {
  isAssistant: boolean;
  children: InferenceMessage["content"];
  chatId: string;
} & (
  | {
      messageId: string;
      isPending: false;
    }
  | { messageId?: undefined; isPending: true }
);

const ChatMessageEntry = ({ children, isAssistant, isPending, chatId, messageId }: ChatMessageEntryProps) => {
  const bgUser = useColorModeValue("gray.100", "gray.700");
  const bgAssistant = useColorModeValue("#DFE8F1", "#42536B");
  const { trigger } = useSWRMutation<
    any,
    any,
    any,
    {
      message_id: string;
      chat_id: string;
      score: number;
    }
  >(API_ROUTES.CHAT_MESSAGE_VOTE, post);
  const handleVote = useCallback(
    (score: number) => {
      if (isPending) {
        return;
      }
      trigger({ chat_id: chatId, message_id: messageId, score });
    },
    [chatId, isPending, messageId, trigger]
  );

  return (
    <BaseMessageEntry
      avatarProps={{
        src: isAssistant ? `/images/temp-avatars/av1.jpg` : "/images/temp-avatars/av1.jpg",
      }}
      bg={isAssistant ? bgAssistant : bgUser}
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      content={children!}
    >
      {isAssistant && !isPending && (
        <MessageInlineEmojiRow>
          <MessageEmojiButton
            emoji={{ name: "+1", count: 0 }}
            checked={false}
            userReacted={false}
            userIsAuthor={false}
            forceHideCount
            onClick={handleVote}
            // onClick={() => react(emoji, !emojiState.user_emojis.includes(emoji))}
          />
          <MessageEmojiButton
            emoji={{ name: "-1", count: 0 }}
            checked={false}
            userReacted={false}
            userIsAuthor={false}
            forceHideCount
            onClick={handleVote}
            // onClick={() => react(emoji, !emojiState.user_emojis.includes(emoji))}
          />
        </MessageInlineEmojiRow>
      )}
    </BaseMessageEntry>
  );
};

async function* iteratorSSE(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }

    const fields = value
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => {
        const colonIdx = line.indexOf(":");
        return [line.slice(0, colonIdx), line.slice(colonIdx + 1).trimStart()];
      });
    yield Object.fromEntries(fields);
  }
}
