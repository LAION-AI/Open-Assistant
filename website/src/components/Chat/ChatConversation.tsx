/* eslint-disable @typescript-eslint/no-explicit-any */
import { Badge, Box, CircularProgress, useBoolean, useToast } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { UseFormGetValues } from "react-hook-form";
import SimpleBar from "simplebar-react";
import { useMessageVote } from "src/hooks/chat/useMessageVote";
import { useBrowserConfig } from "src/hooks/env/BrowserEnv";
import { get, post } from "src/lib/api";
import { handleChatEventStream, PluginIntermediateResponse, QueueInfo } from "src/lib/chat_stream";
import { OasstError } from "src/lib/oasst_api_client";
import { API_ROUTES } from "src/lib/routes";
import {
  ChatConfigFormData,
  ChatItem,
  InferenceMessage,
  InferencePostAssistantMessageParams,
  InferencePostPrompterMessageParams,
} from "src/types/Chat";
import { mutate } from "swr";
import useSWR from "swr";

import { ChatAssistantDraftPager, DraftPickedParams } from "./ChatAssistantDraftPager";
import { ChatConversationTree, LAST_ASSISTANT_MESSAGE_ID } from "./ChatConversationTree";
import { ChatForm } from "./ChatForm";
import { ChatMessageEntryProps, EditPromptParams, PendingMessageEntry } from "./ChatMessageEntry";
import { ChatWarning } from "./ChatWarning";

interface ChatConversationProps {
  chatId: string;
  getConfigValues: UseFormGetValues<ChatConfigFormData>;
}

export const ChatConversation = memo(function ChatConversation({ chatId, getConfigValues }: ChatConversationProps) {
  const { t } = useTranslation("chat");
  const { ENABLE_DRAFTS_WITH_PLUGINS, NUM_GENERATED_DRAFTS } = useBrowserConfig();
  const router = useRouter();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<InferenceMessage[]>([]);
  const [activeThreadTailMessageId, setActiveThreadTailMessageId] = useState<string | null>(null);

  const [streamedDrafts, setStreamedDrafts] = useState<string[]>([]);
  const [draftMessages, setDraftMessages] = useState<InferenceMessage[][]>([]);
  const [isAwaitingMessageSelect, setIsAwaitingMessageSelect] = useBoolean();

  const [streamedResponse, setResponse] = useState<string | null>(null);
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [pluginIntermediateResponse, setPluginIntermediateResponse] = useState<PluginIntermediateResponse | null>(null);
  const [isSending, setIsSending] = useBoolean();
  const [showEncourageMessage, setShowEncourageMessage] = useBoolean(false);

  const toast = useToast();

  const { isLoading: isLoadingMessages, data: chatData } = useSWR<ChatItem>(
    chatId ? API_ROUTES.GET_CHAT(chatId) : null,
    get,
    {
      onSuccess(data) {
        setMessages(data.messages.sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at)));
        setActiveThreadTailMessageId(data.active_thread_tail_message_id);
      },
      onError: (err) => {
        if (err instanceof OasstError && err.httpStatusCode === 404) {
          // chat does not exist, probably deleted
          return router.push("/chat");
        }
        toast({
          title: "Failed to load chat",
          status: "error",
        });
      },
    }
  );

  const createAndFetchAssistantMessage = useCallback(
    async ({ parentId, chatId }: { parentId: string; chatId: string }) => {
      const { model_config_name, plugins, ...sampling_parameters } = getConfigValues();
      const assistant_arg: InferencePostAssistantMessageParams = {
        chat_id: chatId,
        parent_id: parentId,
        model_config_name,
        sampling_parameters,
        plugins,
      };

      let assistant_message: InferenceMessage;
      try {
        assistant_message = await post(API_ROUTES.CREATE_ASSISTANT_MESSAGE, {
          arg: assistant_arg,
        });
      } catch (e) {
        if (e instanceof OasstError) {
          toast({
            title: e.message,
            status: "error",
          });
        }
        setIsSending.off();
        return;
      }

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
          onPending: (data) => {
            setQueueInfo(data);
            setPluginIntermediateResponse(null);
          },
          onPluginIntermediateResponse: setPluginIntermediateResponse,
          onToken: async (text) => {
            setQueueInfo(null);
            if (text != "") {
              setPluginIntermediateResponse(null);
            }
            setResponse(text);
            await new Promise(requestAnimationFrame);
          },
        });
      }
      if (message) {
        setMessages((messages) => [...messages, message!]);
        setActiveThreadTailMessageId(message.id);
      }
      setQueueInfo(null);
      setResponse(null);
      setIsSending.off();
      setShowEncourageMessage.on();
    },
    [getConfigValues, setIsSending, setShowEncourageMessage, toast, setActiveThreadTailMessageId]
  );
  const createAssistantDrafts = useCallback(
    async ({ parentId, chatId }: { parentId: string; chatId: string }) => {
      const { model_config_name, plugins, ...sampling_parameters } = getConfigValues();

      const assistant_arg: InferencePostAssistantMessageParams = {
        chat_id: chatId,
        parent_id: parentId,
        model_config_name: model_config_name,
        sampling_parameters: sampling_parameters,
        plugins: plugins,
      };

      let draft_messages: InferenceMessage[];
      try {
        const promises = Array.from({ length: NUM_GENERATED_DRAFTS }, () =>
          post(API_ROUTES.CREATE_ASSISTANT_MESSAGE, { arg: assistant_arg })
        );

        draft_messages = await Promise.all(promises);
      } catch (err) {
        if (err instanceof OasstError) {
          toast({
            title: err.message,
            status: "error",
          });
        }
        setIsSending.off();
        return;
      }

      setStreamedDrafts(Array(NUM_GENERATED_DRAFTS).fill(""));
      const complete_draft_messages = await Promise.all(
        draft_messages.map(async (draft_message, index) => {
          const { body, status } = await fetch(API_ROUTES.STREAM_CHAT_MESSAGE(chatId, draft_message.id));

          let inference_message: InferenceMessage | null;
          if (status === 204) {
            inference_message = await get(API_ROUTES.GET_MESSAGE(chatId, draft_message.id));
          } else {
            inference_message = await handleChatEventStream({
              stream: body!,
              onError: console.error,
              onPending:
                draft_messages.every((message) => message.state === "pending") && index === 0 ? setQueueInfo : null,
              onPluginIntermediateResponse: null,
              onToken: async (text) => {
                setQueueInfo(null);
                setStreamedDrafts((drafts) => [...drafts.slice(0, index), text, ...drafts.slice(index + 1)]);
                await new Promise(requestAnimationFrame);
              },
            });
          }

          setStreamedDrafts((drafts) => [
            ...drafts.slice(0, index),
            inference_message.content,
            ...drafts.slice(index + 1),
          ]);
          await new Promise(requestAnimationFrame);

          return inference_message;
        })
      );

      setDraftMessages((draftMessages) => [...draftMessages, complete_draft_messages]);

      setQueueInfo(null);
      setIsSending.off();
      setIsAwaitingMessageSelect.on();
    },
    [
      getConfigValues,
      setIsSending,
      setStreamedDrafts,
      setDraftMessages,
      setQueueInfo,
      setIsAwaitingMessageSelect,
      NUM_GENERATED_DRAFTS,
      toast,
    ]
  );

  const { messagesEndRef, scrollableNodeProps, updateEnableAutoScroll, activateAutoScroll } = useAutoScroll(
    messages,
    streamedResponse,
    draftMessages,
    streamedDrafts
  );

  const sendPrompterMessage = useCallback(async () => {
    const content = inputRef.current?.value.trim();
    if (!content || isSending) {
      return;
    }

    if (isAwaitingMessageSelect) {
      return toast({
        title: t("select_chat_notify"),
      });
    }

    setIsSending.on();
    setShowEncourageMessage.off();

    // TODO: maybe at some point we won't need to access the rendered HTML directly, but use react state
    const parentId = document.getElementById(LAST_ASSISTANT_MESSAGE_ID)?.dataset.id ?? null;
    if (parentId !== null) {
      const parent = messages.find((m) => m.id === parentId);
      if (!parent) {
        // we should never reach here
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
      chat_id: chatId,
      content,
      parent_id: parentId,
    };

    let prompter_message: InferenceMessage;
    try {
      prompter_message = await post(API_ROUTES.CREATE_PROMPTER_MESSAGE, { arg: prompter_arg });
    } catch (e) {
      if (e instanceof OasstError) {
        toast({
          title: e.message,
          status: "error",
        });
      }
      setIsSending.off();
      return;
    }
    if (messages.length === 0) {
      // revalidate chat list after creating the first prompter message to make sure the message already has title
      mutate(API_ROUTES.LIST_CHAT);
    }
    setMessages((messages) => [...messages, prompter_message]);

    inputRef.current!.value = "";
    activateAutoScroll();
    // after creating the prompters message, handle the assistant's case
    await createAndFetchAssistantMessage({ parentId: prompter_message.id, chatId });
  }, [
    setIsSending,
    chatId,
    messages,
    createAndFetchAssistantMessage,
    toast,
    isSending,
    isAwaitingMessageSelect,
    setShowEncourageMessage,
    activateAutoScroll,
    t,
  ]);

  const sendVote = useMessageVote();

  const [retryingParentId, setReytryingParentId] = useState<string | null>(null);

  const handleOnRetry = useCallback(
    async (params: { parentId: string; chatId: string }) => {
      setIsSending.on();
      setReytryingParentId(params.parentId);

      const { plugins } = getConfigValues();
      if (
        (!ENABLE_DRAFTS_WITH_PLUGINS && plugins.length !== 0) ||
        NUM_GENERATED_DRAFTS <= 1 ||
        !chatData.allow_data_use
      ) {
        await createAndFetchAssistantMessage(params);
        setReytryingParentId(null);
      } else {
        await createAssistantDrafts(params);
      }
    },
    [
      createAssistantDrafts,
      setIsSending,
      getConfigValues,
      ENABLE_DRAFTS_WITH_PLUGINS,
      NUM_GENERATED_DRAFTS,
      createAndFetchAssistantMessage,
      chatData?.allow_data_use,
    ]
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
        await createAndFetchAssistantMessage({ parentId: prompter_message.id, chatId });
      }

      setReytryingParentId(null);
    },
    [createAndFetchAssistantMessage, isSending, setIsSending]
  );

  const handleDraftPicked = useCallback(
    async ({ chatId, regenIndex, messageIndex }: DraftPickedParams) => {
      if (!isAwaitingMessageSelect) {
        return toast({
          title: t("drafts_generating_notify"),
        });
      }

      await post(API_ROUTES.CHAT_MESSAGE_EVAL, {
        arg: {
          chat_id: chatId,
          message_id: draftMessages[regenIndex][messageIndex].id,
          inferior_message_ids: draftMessages[regenIndex]
            .filter((draft) => draft.id !== draftMessages[regenIndex][messageIndex].id)
            .map((draft) => draft.id),
        },
      });

      setMessages([...messages, ...draftMessages[regenIndex]]);
      setActiveThreadTailMessageId(draftMessages[regenIndex][messageIndex].id);
      setIsAwaitingMessageSelect.off();
      setStreamedDrafts(null);
      setDraftMessages([]);
      setReytryingParentId(null);
      setShowEncourageMessage.on();
    },
    [
      isAwaitingMessageSelect,
      setMessages,
      messages,
      draftMessages,
      setIsAwaitingMessageSelect,
      setStreamedDrafts,
      setDraftMessages,
      setReytryingParentId,
      setShowEncourageMessage,
      setActiveThreadTailMessageId,
      toast,
      t,
    ]
  );

  return (
    <Box
      pt="4"
      px="2"
      gap="1"
      height="full"
      minH="0"
      display="flex"
      flexDirection="column"
      flexGrow="1"
      _light={{
        bg: "gray.50",
      }}
      _dark={{
        bg: "blackAlpha.300",
      }}
    >
      <Box height="full" minH={0} position="relative">
        {isLoadingMessages && <CircularProgress isIndeterminate size="20px" mx="auto" />}
        <SimpleBar
          onMouseDown={updateEnableAutoScroll}
          scrollableNodeProps={scrollableNodeProps}
          style={{ maxHeight: "100%", height: "100%", minHeight: "0", paddingBottom: "1rem" }}
          classNames={{
            contentEl: "space-y-4 mx-4 flex flex-col overflow-y-auto items-center",
          }}
        >
          <ChatConversationTree
            messages={messages}
            onVote={handleOnVote}
            onRetry={handleOnRetry}
            isSending={isSending}
            retryingParentId={retryingParentId}
            activeThreadTailMessageId={activeThreadTailMessageId}
            onEditPrompt={handleEditPrompt}
            showEncourageMessage={showEncourageMessage}
            onEncourageMessageClose={setShowEncourageMessage.off}
            showFeedbackOptions={chatData?.allow_data_use}
          ></ChatConversationTree>
          {isSending && streamedResponse && <PendingMessageEntry isAssistant content={streamedResponse} />}
          {(isSending || isAwaitingMessageSelect) &&
          ((Array.isArray(streamedDrafts) && streamedDrafts.length) ||
            (Array.isArray(draftMessages) && draftMessages.length)) ? (
            <ChatAssistantDraftPager
              chatId={chatId}
              streamedDrafts={streamedDrafts}
              draftMessageRegens={draftMessages}
              onDraftPicked={handleDraftPicked}
              onRetry={handleOnRetry}
            />
          ) : null}
          <div ref={messagesEndRef} style={{ height: 0 }}></div>
        </SimpleBar>

        {queueInfo && (
          <Badge position="absolute" bottom="0" left="50%" transform="translate(-50%)">
            {t("queue_info", queueInfo)}
          </Badge>
        )}
        {pluginIntermediateResponse && pluginIntermediateResponse.currentPluginThought && (
          <Box
            position="absolute"
            bottom="0"
            left="50%"
            transform="translate(-50%)"
            display="flex"
            flexDirection="row"
            gap="1"
            justifyContent="center"
            alignItems="center"
          >
            <Box
              bg="purple.700"
              color="white"
              px="2"
              py="2.5px"
              borderRadius="8px"
              maxWidth="50vw"
              fontSize="11"
              fontWeight="bold"
              isTruncated
            >
              {pluginIntermediateResponse.currentPluginThought}
            </Box>
          </Box>
        )}
      </Box>
      <ChatForm ref={inputRef} isSending={isSending} onSubmit={sendPrompterMessage}></ChatForm>
      <ChatWarning />
    </Box>
  );
});

const useAutoScroll = (
  messages: InferenceMessage[],
  streamedResponse: string | null,
  draftMessages: InferenceMessage[][],
  streamedDrafts: string[] | null
) => {
  const enableAutoScroll = useRef(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const updateEnableAutoScroll = useCallback(() => {
    const container = chatContainerRef.current;
    if (!container) {
      return;
    }

    const isEnable = container.scrollHeight - container.scrollTop - container.clientHeight < 10;
    enableAutoScroll.current = isEnable;
  }, []);

  const activateAutoScroll = useCallback(() => {
    enableAutoScroll.current = true;
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (!enableAutoScroll.current) {
      return;
    }

    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedResponse, draftMessages, streamedDrafts]);

  const scrollableNodeProps = useMemo(
    () => ({
      ref: chatContainerRef,
      onWheel: updateEnableAutoScroll,
      // onScroll: handleOnScroll,
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === "ArrowUp" || e.key === "ArrowDown") {
          updateEnableAutoScroll();
        }
      },
      onTouchMove: updateEnableAutoScroll,
      onMouseDown: updateEnableAutoScroll(),
    }),
    [updateEnableAutoScroll]
  );

  return { messagesEndRef, scrollableNodeProps, updateEnableAutoScroll, activateAutoScroll };
};
