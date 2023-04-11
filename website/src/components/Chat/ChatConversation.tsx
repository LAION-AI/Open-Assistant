/* eslint-disable @typescript-eslint/no-explicit-any */
import { Button, CircularProgress, Flex, Icon, Text, useBoolean, useColorModeValue } from "@chakra-ui/react";
import { XCircle } from "lucide-react";
import router from "next/router";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode, useCallback, useMemo, useRef, useState } from "react";
import { useFormContext } from "react-hook-form";
import { useMessageVote } from "src/hooks/chat/useMessageVote";
import { get, post } from "src/lib/api";
import { handleChatEventStream, QueueInfo } from "src/lib/chat_stream";
import { API_ROUTES, ROUTES } from "src/lib/routes";
import {
  ChatConfigForm,
  ChatItem,
  InferenceMessage,
  InferencePostAssistantMessageParams,
  InferencePostPrompterMessageParams,
} from "src/types/Chat";
import useSWR, { mutate } from "swr";

import { BaseMessageEntry } from "../Messages/BaseMessageEntry";
import { MessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { ChatForm } from "./ChatForm";
import { WorkParametersDisplay } from "./WorkParameters";

interface ChatConversationProps {
  chatId: string | null; // will be null when render on chat list page (/chat)
}

export const ChatConversation = ({ chatId: chatIdProps }: ChatConversationProps) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<InferenceMessage[]>([]);

  const [streamedResponse, setResponse] = useState<string | null>(null);
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [isSending, setIsSending] = useBoolean();

  // calculate the current thread as always going down the newest child in the tree
  const currentThread: InferenceMessage[] = useMemo(() => {
    if (!messages.length) return [];
    // sort dates latest first
    const sortedMessages = messages.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
    // find the root message without parent_id
    const root = sortedMessages.find((m) => m.parent_id === null)!;
    const threadMessages = [root];
    let current: InferenceMessage | null = root;
    while (current) {
      const next = sortedMessages.find((m) => m.parent_id === current!.id);
      if (next) {
        threadMessages.push(next);
        current = next;
      } else {
        current = null;
      }
    }
    return threadMessages;
  }, [messages]);

  useSWR<ChatItem>(chatIdProps === null ? null : API_ROUTES.GET_CHAT(chatIdProps), get, {
    onSuccess: (chat) => setMessages(chat.messages.sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at))),
  });
  const { getValues: getFormValues } = useFormContext<ChatConfigForm>();

  const initiate_assistant_message = useCallback(
    async (parent_id: string, chatId: string) => {
      const { model_config_name, ...sampling_parameters } = getFormValues();
      const assistant_arg: InferencePostAssistantMessageParams = {
        chat_id: chatId,
        parent_id,
        model_config_name,
        sampling_parameters,
      };

      const assistant_message: InferenceMessage = await post(API_ROUTES.CREATE_ASSISTANT_MESSAGE, {
        arg: assistant_arg,
      });

      // we have to do this manually since we want to stream the chunks
      // there is also EventSource, but it is callback based
      const { body, status } = await fetch(API_ROUTES.STREAM_CHAT_MESSAGE(chatId, assistant_message.id));

      let message: InferenceMessage | null;
      if (status === 204) {
        // message already processed, get it immediately
        message = await get(API_ROUTES.GET_MESSAGE(chatId, assistant_message.id));
      } else {
        message = await handleChatEventStream({
          stream: body!,
          onError: console.error,
          onPending: setQueueInfo,
          onToken: async (text) => {
            setQueueInfo(null);
            setResponse(text);
            await new Promise(requestAnimationFrame);
          },
        });
      }
      if (message) {
        setMessages((messages) => [...messages, message!]);
      }
      setQueueInfo(null);
      setResponse(null);
      setIsSending.off();
    },
    [getFormValues, setIsSending]
  );
  const send = useCallback(async () => {
    const content = inputRef.current?.value.trim();
    if (!content) {
      return;
    }
    setIsSending.on();
    let currentChatId = chatIdProps;
    if (currentChatId === null) {
      const chat: ChatItem = await post(API_ROUTES.LIST_CHAT);
      // setChatId(chat.id);
      currentChatId = chat.id;
    }

    // find last VALID assistant message
    const parent_id =
      currentThread
        .slice()
        .reverse()
        .find((m) => m.role === "assistant" && m.state === "complete")?.id ?? null;

    const prompter_arg: InferencePostPrompterMessageParams = {
      chat_id: currentChatId,
      content,
      parent_id,
    };

    const prompter_message: InferenceMessage = await post(API_ROUTES.CREATE_PROMPTER_MESSAGE, { arg: prompter_arg });
    mutate(API_ROUTES.LIST_CHAT); // revalidte chat list after create prompter message to make sure the message already has title
    setMessages((messages) => [...messages, prompter_message]);

    await initiate_assistant_message(prompter_message.id, currentChatId);
    await router.push(ROUTES.CHAT(currentChatId));
  }, [setIsSending, chatIdProps, currentThread, initiate_assistant_message]);

  const sendVote = useMessageVote();

  const handleOnRetry = useCallback(
    (messageId: string, chatId: string) => {
      setIsSending.on();
      initiate_assistant_message(messageId, chatId);
    },
    [initiate_assistant_message, setIsSending]
  );

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

  const entries = useMemo(
    () =>
      currentThread.map((message) => (
        <ChatMessageEntry
          key={message.id}
          isAssistant={message.role === "assistant"}
          messageId={message.id}
          parentId={message.parent_id}
          chatId={message.chat_id}
          score={message.score}
          state={message.state}
          onVote={handleOnVote}
          onRetry={handleOnRetry}
          isSending={isSending}
          workParameters={message.work_parameters}
        >
          {message.content}
        </ChatMessageEntry>
      )),
    [handleOnVote, currentThread, handleOnRetry, isSending]
  );

  return (
    <Flex flexDir="column" gap={4}>
      {entries}
      {isSending && streamedResponse && <PendingMessageEntry isAssistant content={streamedResponse} />}

      <ChatForm ref={inputRef} isSending={isSending} onSubmit={send} queueInfo={queueInfo}></ChatForm>
    </Flex>
  );
};

type ChatMessageEntryProps = {
  isAssistant: boolean;
  children: InferenceMessage["content"];
  state: InferenceMessage["state"];
  chatId: string;
  messageId: string;
  parentId: InferenceMessage["parent_id"];
  workParameters?: InferenceMessage["work_parameters"];
  score: number;
  onVote: (data: { newScore: number; oldScore: number; chatId: string; messageId: string }) => void;
  onRetry?: (messageId: string, chatId: string) => void;
  isSending?: boolean;
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
  parentId,
  score,
  state,
  onVote,
  onRetry,
  isSending,
  workParameters,
}: ChatMessageEntryProps) {
  const { t } = useTranslation("common");
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

  const handleRetry = useCallback(() => {
    if (onRetry && parentId) {
      onRetry(parentId, chatId);
    }
  }, [chatId, onRetry, parentId]);

  return (
    <PendingMessageEntry isAssistant={isAssistant} content={children!}>
      {isAssistant && (
        <MessageInlineEmojiRow>
          {(state === "pending" || state === "in_progress") && (
            <CircularProgress isIndeterminate size="20px" title={state} />
          )}
          {(state === "aborted_by_worker" || state === "cancelled" || state === "timeout") && (
            <>
              <Icon as={XCircle} color="red" />
              <Text color="red">{`Error: ${state}`}</Text>
              {onRetry && !isSending && <Button onClick={handleRetry}>{t("retry")}</Button>}
            </>
          )}
          {state === "complete" && (
            <>
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
              {workParameters && <WorkParametersDisplay parameters={workParameters} />}
            </>
          )}
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
  const bgUser = useColorModeValue("white", "gray.700");
  const bgAssistant = useColorModeValue("#DFE8F1", "#42536B");
  const { data: session } = useSession();
  const image = session?.user?.image;

  const avatarProps = useMemo(
    () => ({ src: isAssistant ? `/images/logos/logo.png` : image ?? "/images/temp-avatars/av1.jpg" }),
    [isAssistant, image]
  );

  return (
    <BaseMessageEntry
      avatarProps={avatarProps}
      bg={isAssistant ? bgAssistant : bgUser}
      content={content || ""}
      width="full"
      maxWidth="full"
    >
      {children}
    </BaseMessageEntry>
  );
};
