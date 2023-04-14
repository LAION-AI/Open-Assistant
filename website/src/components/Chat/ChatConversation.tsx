/* eslint-disable @typescript-eslint/no-explicit-any */
import { Flex, useBoolean, useToast } from "@chakra-ui/react";
import router from "next/router";
import { memo, useCallback, useRef, useState } from "react";
import { useFormContext } from "react-hook-form";
import { useMessageVote } from "src/hooks/chat/useMessageVote";
import { get, post } from "src/lib/api";
import { handleChatEventStream, QueueInfo } from "src/lib/chat_stream";
import { API_ROUTES, ROUTES } from "src/lib/routes";
import {
  ChatConfigFormData,
  ChatItem,
  InferenceMessage,
  InferencePostAssistantMessageParams,
  InferencePostPrompterMessageParams,
} from "src/types/Chat";
import { mutate } from "swr";

import { useChatContext } from "./ChatContext";
import { ChatConversationTree, LAST_ASSISTANT_MESSAGE_ID } from "./ChatConversationTree";
import { ChatForm } from "./ChatForm";
import { ChatMessageEntryProps, EditPromptParams, PendingMessageEntry } from "./ChatMessageEntry";

interface ChatConversationProps {
  chatId: string | null; // will be null when render on chat list page (/chat)
}

export const ChatConversation = memo(function ChatConversation({ chatId: chatIdProps }: ChatConversationProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<InferenceMessage[]>(useChatContext().messages);

  const [streamedResponse, setResponse] = useState<string | null>(null);
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [isSending, setIsSending] = useBoolean();

  const { getValues: getFormValues } = useFormContext<ChatConfigFormData>();

  const initiate_assistant_message = useCallback(
    async ({ parentId, chatId }: { parentId: string; chatId: string }) => {
      const { model_config_name, ...sampling_parameters } = getFormValues();
      console.log(`chatId`, chatId);
      const assistant_arg: InferencePostAssistantMessageParams = {
        chat_id: chatId,
        parent_id: parentId,
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
  const toast = useToast();
  const send = useCallback(async () => {
    const content = inputRef.current?.value.trim();
    if (!content) {
      return;
    }
    setIsSending.on();
    inputRef.current!.value = "";
    let currentChatId = chatIdProps;
    if (currentChatId === null) {
      const chat: ChatItem = await post(API_ROUTES.LIST_CHAT);
      currentChatId = chat.id;
    }

    const parentId = document.getElementById(LAST_ASSISTANT_MESSAGE_ID)?.dataset.id ?? null;
    if (parentId !== null) {
      const parent = messages.find((m) => m.id === parentId);
      if (!parent) {
        return console.error("Parent message not found", parentId);
      }
      if (parent!.state !== "complete") {
        return toast({
          title: "You are trying reply to a message that is not complete yet.",
        });
      }
      // parent is exist and completed here, so we can send the message
    }

    const prompter_arg: InferencePostPrompterMessageParams = {
      chat_id: currentChatId,
      content,
      parent_id: parentId,
    };

    const prompter_message: InferenceMessage = await post(API_ROUTES.CREATE_PROMPTER_MESSAGE, { arg: prompter_arg });
    mutate(API_ROUTES.LIST_CHAT); // revalidte chat list after create prompter message to make sure the message already has title
    setMessages((messages) => [...messages, prompter_message]);

    await initiate_assistant_message({ parentId: prompter_message.id, chatId: currentChatId });
    router.push(ROUTES.CHAT(currentChatId));
  }, [setIsSending, chatIdProps, initiate_assistant_message, messages, toast]);

  const sendVote = useMessageVote();

  const [retryingParentId, setReytryingParentId] = useState<string | null>(null);

  const handleOnRetry = useCallback(
    async (params: { parentId: string; chatId: string }) => {
      setIsSending.on();
      setReytryingParentId(params.parentId);
      await initiate_assistant_message(params);
      setReytryingParentId(null);
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

  const handleEditPrompt = useCallback(
    async ({ chatId, parentId, content }: EditPromptParams) => {
      if (!content || isSending) {
        return;
      }

      setIsSending.on();
      setReytryingParentId(parentId);
      const prompter_arg: InferencePostPrompterMessageParams = {
        chat_id: chatId,
        content,
        parent_id: parentId,
      };

      let prompter_message: InferenceMessage | null = null;
      const dummyMessage: InferenceMessage = {
        id: "__dummy__",
        ...prompter_arg,
        created_at: new Date().toISOString(),
        role: "prompter",
        state: "complete",
        score: 0,
        reports: [],
      };

      try {
        // push the dummy message first to avoid layout shift
        setMessages((messages) => [...messages, dummyMessage]);
        prompter_message = await post(API_ROUTES.CREATE_PROMPTER_MESSAGE, { arg: prompter_arg });
        // filter out the dummy message and push the real one
        setMessages((messages) => [...messages.filter((m) => m.id !== "__dummy__"), prompter_message!]);
      } catch {
        // revert on any error
        // TODO consider to trigger notification
        setMessages((messages) => messages.filter((m) => m.id !== "__dummy__"));
      }

      if (prompter_message) {
        await initiate_assistant_message({ parentId: prompter_message.id, chatId: chatId });
      }

      setReytryingParentId(null);
    },
    [initiate_assistant_message, isSending, setIsSending]
  );

  return (
    <Flex flexDir="column" gap={4}>
      <ChatConversationTree
        messages={messages}
        onVote={handleOnVote}
        onRetry={handleOnRetry}
        isSending={isSending}
        retryingParentId={retryingParentId}
        onEditPromtp={handleEditPrompt}
      ></ChatConversationTree>
      {isSending && streamedResponse && <PendingMessageEntry isAssistant content={streamedResponse} />}

      <ChatForm ref={inputRef} isSending={isSending} onSubmit={send} queueInfo={queueInfo}></ChatForm>
    </Flex>
  );
});
