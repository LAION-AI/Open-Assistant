import { Button, CircularProgress, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import { XCircle } from "lucide-react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode, useCallback, useMemo } from "react";
import { InferenceMessage } from "src/types/Chat";

import { BaseMessageEntry } from "../Messages/BaseMessageEntry";
import { MessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { WorkParametersDisplay } from "./WorkParameters";

export type ChatMessageEntryProps = {
  message: InferenceMessage;
  onVote: (data: { newScore: number; oldScore: number; chatId: string; messageId: string }) => void;
  onRetry?: (messageId: string, chatId: string) => void;
  isSending?: boolean;
};

export const ChatMessageEntry = memo(function ChatMessageEntry({
  onVote,
  onRetry,
  isSending,
  message,
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
      onRetry(parentId, chatId);
    }
  }, [chatId, onRetry, parentId]);
  const isAssistant = message.role === "assistant";
  return (
    <PendingMessageEntry isAssistant={isAssistant} content={content!}>
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
            </>
          )}
        </MessageInlineEmojiRow>
      )}
      {work_parameters && <WorkParametersDisplay parameters={work_parameters} />}
    </PendingMessageEntry>
  );
});

type PendingMessageEntryProps = {
  isAssistant: boolean;
  content: string;
  children?: ReactNode;
};

export const PendingMessageEntry = ({ content, isAssistant, children }: PendingMessageEntryProps) => {
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
