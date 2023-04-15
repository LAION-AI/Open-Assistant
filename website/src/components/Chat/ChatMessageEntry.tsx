import {
  Box,
  Button,
  CircularProgress,
  Flex,
  Icon,
  Text,
  Textarea,
  useBoolean,
  useColorModeValue,
  useOutsideClick,
} from "@chakra-ui/react";
import { Check, Edit, RotateCcw, ThumbsUp, X, XCircle } from "lucide-react";
import { ThumbsDown } from "lucide-react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { forwardRef, KeyboardEvent, memo, ReactNode, useCallback, useMemo, useRef } from "react";
import { InferenceMessage } from "src/types/Chat";

import { BaseMessageEntry } from "../Messages/BaseMessageEntry";
import { BaseMessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { WorkParametersDisplay } from "./WorkParameters";

export type EditPromptParams = { parentId: string; chatId: string; content: string };

export type ChatMessageEntryProps = {
  message: InferenceMessage;
  onVote: (data: { newScore: number; oldScore: number; chatId: string; messageId: string }) => void;
  onRetry?: (params: { parentId: string; chatId: string }) => void;
  isSending?: boolean;
  pagingSlot?: ReactNode;
  onEditPromtp?: (params: EditPromptParams) => void;
  canRetry?: boolean;
  id?: string;
  "data-id"?: string;
};

export const ChatMessageEntry = memo(function ChatMessageEntry({
  onVote,
  onRetry,
  isSending,
  message,
  pagingSlot,
  onEditPromtp,
  canRetry,
  ...props
}: ChatMessageEntryProps) {
  const { t } = useTranslation("common");
  const { chat_id: chatId, parent_id: parentId, id: messageId, content, score, state, work_parameters } = message;
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
      onRetry({ parentId, chatId });
    }
  }, [chatId, onRetry, parentId]);
  const isAssistant = message.role === "assistant";
  const [isEditing, setIsEditing] = useBoolean(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleEditSubmit = useCallback(() => {
    if (onEditPromtp && inputRef.current?.value && parentId !== null) {
      onEditPromtp({ parentId, chatId, content: inputRef.current?.value });
    }
    setIsEditing.off();
  }, [chatId, onEditPromtp, parentId, setIsEditing]);

  const ref = useRef<HTMLDivElement>(null);

  useOutsideClick({
    ref,
    handler: setIsEditing.off,
  });

  const handleKeydown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsEditing.off();
      }
      if (e.key === "Enter" && !e.shiftKey) {
        handleEditSubmit();
      }
    },
    [handleEditSubmit, setIsEditing]
  );

  return (
    <PendingMessageEntry ref={ref} {...props} isAssistant={isAssistant} content={isEditing ? "" : content!}>
      {!isAssistant && parentId !== null && (
        <Box position="absolute" top={{ base: "4", md: 0 }} style={{ insetInlineEnd: `0.5rem` }}>
          {isEditing ? (
            <MessageInlineEmojiRow spacing="0">
              <BaseMessageEmojiButton emoji={Check} onClick={handleEditSubmit}></BaseMessageEmojiButton>
              <BaseMessageEmojiButton emoji={X} onClick={setIsEditing.off}></BaseMessageEmojiButton>
            </MessageInlineEmojiRow>
          ) : (
            <BaseMessageEmojiButton emoji={Edit} onClick={setIsEditing.on}></BaseMessageEmojiButton>
          )}
        </Box>
      )}
      {isEditing && (
        <Box mx={{ md: "-15px" }} mt={{ md: 2 }}>
          <Textarea
            defaultValue={content || ""}
            ref={inputRef}
            onKeyDown={handleKeydown}
            bg="gray.100"
            borderRadius="xl"
            _dark={{
              bg: "gray.800",
            }}
          ></Textarea>
        </Box>
      )}
      {!isEditing && (
        <Flex justifyContent={pagingSlot ? "space-between" : "end"} mt="1">
          {pagingSlot}
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
                  {canRetry && <BaseMessageEmojiButton emoji={RotateCcw} onClick={handleRetry} />}
                  <BaseMessageEmojiButton emoji={ThumbsUp} checked={score === 1} onClick={handleThumbsUp} />
                  <BaseMessageEmojiButton emoji={ThumbsDown} checked={score === -1} onClick={handleThumbsDown} />
                </>
              )}
            </MessageInlineEmojiRow>
          )}
        </Flex>
      )}
      {work_parameters && <WorkParametersDisplay parameters={work_parameters} />}
    </PendingMessageEntry>
  );
});

type PendingMessageEntryProps = {
  isAssistant: boolean;
  content: string;
  children?: ReactNode;
  id?: string;
  "data-id"?: string;
};

export const PendingMessageEntry = forwardRef<HTMLDivElement, PendingMessageEntryProps>(function PendingMessageEntry(
  { content, isAssistant, children, ...props },
  ref
) {
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
      ref={ref}
      avatarProps={avatarProps}
      bg={isAssistant ? bgAssistant : bgUser}
      content={content || ""}
      width="full"
      maxWidth="full"
      {...props}
    >
      {children}
    </BaseMessageEntry>
  );
});

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
