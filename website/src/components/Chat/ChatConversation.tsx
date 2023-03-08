/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Flex, Textarea, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode, useCallback, useMemo, useRef, useState } from "react";
import { get, post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { InferenceMessage, InferencePostMessageResponse } from "src/types/Chat";
import useSWRImmutable from "swr/immutable";
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

  useSWRImmutable<InferenceMessage[]>(API_ROUTES.GET_CHAT_MESSAGES(chatId), get, {
    onSuccess: setMessages,
  });

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

    // find last assistant message, is usually last message but not always
    const parent_id =
      messages
        .slice()
        .reverse()
        .find((m) => m.role === "assistant")?.id ?? null;
    const response: InferencePostMessageResponse = await post(API_ROUTES.CREATE_CHAT_MESSAGE, {
      arg: { chat_id: chatId, content, parent_id },
    });

    setMessages((messages) => [...messages, response.prompter_message]);

    // we have to do this manually since we want to stream the chunks
    // there is also EventSource, but it is callback based
    const { body } = await fetch(API_ROUTES.STREAM_CHAT_MESSAGE(chatId, response.assistant_message.id));
    let responseMessage = "";
    for await (const { data } of iteratorSSE(body)) {
      const text = JSON.parse(data).token.text;
      responseMessage += text;
      setResponse(responseMessage);
      // wait for re-render
      await new Promise(requestAnimationFrame);
    }

    setMessages((old) => [...old, { ...response.assistant_message, content: responseMessage, score: 0 }]);
    setResponse(null);
  }, [chatId, messages]);

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

  const handleOnVote: ChatMessageEntryProps["onVote"] = useCallback(
    async ({ chatId, messageId, newScore, oldScore }) => {
      // immediately set score
      setMessages((messages) =>
        messages.map((message) => {
          return message.id !== messageId ? message : { ...message, score: newScore };
        })
      );
      try {
        await trigger({ chat_id: chatId, message_id: messageId, score: newScore });
      } catch {
        // TODO maybe we should trigger a toast or something
        // revert on any error
        setMessages((messages) =>
          messages.map((message) => {
            return message.id !== messageId ? message : { ...message, score: oldScore };
          })
        );
      }
    },
    [trigger]
  );

  const entires = useMemo(
    () =>
      messages.map((message) => (
        <ChatMessageEntry
          key={message.id}
          isAssistant={message.role === "assistant"}
          messageId={message.id}
          chatId={chatId}
          score={message.score}
          onVote={handleOnVote}
        >
          {message.content}
        </ChatMessageEntry>
      )),
    [chatId, handleOnVote, messages]
  );

  return (
    <Flex flexDir="column" gap={4} overflowY="auto">
      {entires}
      {streamedResponse ? (
        <PendingMessageEntry isAssistant content={streamedResponse} />
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
  messageId: string;
  score: number;
  onVote: (data: { newScore: number; oldScore: number; chatId: string; messageId: string }) => void;
};

const getNewScore = (emoji: "+1" | "-1", currentScore: number) => {
  if (emoji === "+1") {
    if (currentScore === 1) {
      return 0;
    }
    return 1;
  }
  // emoji is -1
  if (currentScore === -1) {
    return 0;
  }
  return -1;
};

const ChatMessageEntry = memo(function ChatMessageEntry({
  children,
  isAssistant,
  chatId,
  messageId,
  score,
  onVote,
}: ChatMessageEntryProps) {
  const handleVote = useCallback(
    (emoji: "+1" | "-1") => {
      const newScore = getNewScore(emoji, score);
      onVote({ newScore, chatId, messageId, oldScore: score });
    },
    [chatId, messageId, onVote, score]
  );

  const handleThumbsUp = useCallback(() => {
    handleVote("+1");
  }, [handleVote]);

  const handleThumbsDown = useCallback(() => {
    handleVote("-1");
  }, [handleVote]);

  return (
    <PendingMessageEntry isAssistant={isAssistant} content={children!}>
      {isAssistant && (
        <MessageInlineEmojiRow>
          <MessageEmojiButton
            emoji={{ name: "+1", count: 0 }}
            checked={score === 1}
            userReacted={false}
            userIsAuthor={false}
            forceHideCount
            onClick={handleThumbsUp}
          />
          <MessageEmojiButton
            emoji={{ name: "-1", count: 0 }}
            checked={score === -1}
            userReacted={false}
            userIsAuthor={false}
            forceHideCount
            onClick={handleThumbsDown}
          />
        </MessageInlineEmojiRow>
      )}
    </PendingMessageEntry>
  );
});

type PendingMessageEntryProps = {
  isAssistant: boolean;
  content: string;
  children?: ReactNode;
};

const PendingMessageEntry = ({ content, isAssistant, children }: PendingMessageEntryProps) => {
  const bgUser = useColorModeValue("gray.100", "gray.700");
  const bgAssistant = useColorModeValue("#DFE8F1", "#42536B");
  return (
    <BaseMessageEntry
      avatarProps={{
        src: isAssistant ? `/images/logos/logo.png` : "/images/temp-avatars/av1.jpg",
      }}
      bg={isAssistant ? bgAssistant : bgUser}
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      content={content!}
    >
      {children}
    </BaseMessageEntry>
  );
};

async function* iteratorSSE(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value: string | undefined = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }
    if (!value) {
      continue;
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
