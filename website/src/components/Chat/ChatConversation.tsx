/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, Flex, Textarea, useBoolean, useColorModeValue } from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode, useCallback, useMemo, useRef, useState } from "react";
import { useMessageVote } from "src/hooks/chat/useMessageVote";
import { get, post } from "src/lib/api";
import { handleChatEventStream, QueueInfo } from "src/lib/chat_stream";
import { API_ROUTES } from "src/lib/routes";
import { ChatItem, InferenceMessage, InferencePostMessageResponse } from "src/types/Chat";
import useSWR from "swr";

import { BaseMessageEntry } from "../Messages/BaseMessageEntry";
import { MessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { QueueInfoMessage } from "./QueueInfoMessage";
interface ChatConversationProps {
  chatId: string;
}

export const ChatConversation = ({ chatId }: ChatConversationProps) => {
  const { t } = useTranslation("common");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const [messages, setMessages] = useState<InferenceMessage[]>([]);
  const [streamedResponse, setResponse] = useState<string | null>(null);
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [isSending, setIsSending] = useBoolean();

  useSWR<ChatItem>(API_ROUTES.GET_CHAT(chatId), get, { onSuccess: (chat) => setMessages(chat.messages) });

  const send = useCallback(async () => {
    const content = inputRef.current?.value.trim();
    if (!content || !chatId) {
      return;
    }
    setIsSending.on();

    // find last assistant message, is usually last message but not always
    // TODO: the inference server does not return the messages sorted, this is only a best guess
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
    const { body, status } = await fetch(API_ROUTES.STREAM_CHAT_MESSAGE(chatId, response.assistant_message.id));

    let message: InferenceMessage;
    if (status === 204) {
      // message already processed, get it immediately
      message = await get(API_ROUTES.GET_MESSAGE(chatId, response.assistant_message.id));
    } else {
      message = await handleChatEventStream({
        stream: body,
        onError: console.error,
        onPending: setQueueInfo,
        onToken: async (text) => {
          setQueueInfo(null);
          setResponse(text);
          await new Promise(requestAnimationFrame);
        },
      });
    }
    setMessages((messages) => [...messages, message]);
    setQueueInfo(null);
    setResponse(null);
    setIsSending.off();
  }, [chatId, messages, setIsSending]);

  const sendVote = useMessageVote();

  const handleOnVote: ChatMessageEntryProps["onVote"] = useCallback(
    async ({ chatId, messageId, newScore, oldScore }) => {
      // immediately set score
      setMessages((messages) =>
        messages.map((message) => {
          return message.id !== messageId ? message : { ...message, score: newScore };
        })
      );
      try {
        await sendVote({ chat_id: chatId, message_id: messageId, score: newScore });
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
    [sendVote]
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
    <Flex flexDir="column" gap={4}>
      {entires}
      {isSending && streamedResponse && <PendingMessageEntry isAssistant content={streamedResponse} />}
      <Textarea ref={inputRef} autoFocus={!isSending} />
      <Button
        onClick={send}
        isLoading={isSending}
        spinner={queueInfo ? <QueueInfoMessage info={queueInfo} /> : undefined}
      >
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
  const { data: session } = useSession();
  const image = session?.user?.image;

  const avatarProps = useMemo(
    () => ({
      src: isAssistant ? `/images/logos/logo.png` : image ?? "/images/temp-avatars/av1.jpg",
    }),
    [isAssistant, image]
  );

  return (
    <BaseMessageEntry
      avatarProps={avatarProps}
      bg={isAssistant ? bgAssistant : bgUser}
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      content={content!}
    >
      {children}
    </BaseMessageEntry>
  );
};
