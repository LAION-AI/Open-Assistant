import { Box, Flex } from "@chakra-ui/react";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { InferenceMessage } from "src/types/Chat";

import { BaseMessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { ChatAssistantDraftViewer } from "./ChatAssistantDraftViewer";

export type DraftPickedParams = { chatId: string; regenIndex: number; messageIndex: number };

type OnDraftPickedFn = (params: DraftPickedParams) => void;
type OnRetryFn = (params: { parentId: string; chatId: string }) => void;

type ChatAssistantDraftPagerProps = {
  chatId: string;
  streamedDrafts: string[];
  draftMessageRegens: InferenceMessage[][];
  onDraftPicked: OnDraftPickedFn;
  onRetry: OnRetryFn;
};

export const ChatAssistantDraftPager = ({
  chatId,
  streamedDrafts,
  draftMessageRegens,
  onDraftPicked,
  onRetry,
}: ChatAssistantDraftPagerProps) => {
  const [isComplete, setIsComplete] = useState(false);
  const [regenIndex, setRegenIndex] = useState<number>(0);

  useEffect(() => {
    const allMessagesComplete =
      regenIndex < draftMessageRegens.length &&
      draftMessageRegens[regenIndex]?.length !== 0 &&
      draftMessageRegens[regenIndex].every((message) =>
        ["complete", "aborted_by_worker", "cancelled", "timeout"].includes(message.state)
      );
    setIsComplete(allMessagesComplete);
  }, [regenIndex, draftMessageRegens]);

  const handlePrevious = useCallback(() => {
    setRegenIndex(regenIndex > 0 ? regenIndex - 1 : regenIndex);
  }, [setRegenIndex, regenIndex]);

  const handleNext = useCallback(() => {
    setRegenIndex(regenIndex < draftMessageRegens.length - 1 ? regenIndex + 1 : regenIndex);
  }, [setRegenIndex, regenIndex, draftMessageRegens]);

  const handleRetry = useCallback(() => {
    if (onRetry && regenIndex < draftMessageRegens.length && draftMessageRegens[regenIndex]?.length !== 0) {
      onRetry({
        parentId: draftMessageRegens[regenIndex][0].parent_id,
        chatId: draftMessageRegens[regenIndex][0].chat_id,
      });
      setRegenIndex(draftMessageRegens.length);
    }
  }, [onRetry, regenIndex, draftMessageRegens, setRegenIndex]);

  const handleDraftPicked = useCallback(
    (messageIndex: number) => {
      onDraftPicked({ chatId, regenIndex, messageIndex });
    },
    [chatId, regenIndex, onDraftPicked]
  );

  return (
    <ChatAssistantDraftViewer
      streamedDrafts={streamedDrafts}
      isComplete={isComplete}
      draftMessages={draftMessageRegens[Math.min(draftMessageRegens.length - 1, regenIndex)]}
      onDraftPicked={handleDraftPicked}
      pager={
        isComplete ? (
          <Flex justifyContent={"space-between"}>
            <>
              <MessageInlineEmojiRow gap="0.5">
                <BaseMessageEmojiButton emoji={ChevronLeft} onClick={handlePrevious} isDisabled={regenIndex === 0} />
                <Box fontSize="xs">{`${regenIndex + 1}/${draftMessageRegens.length}`}</Box>
                <BaseMessageEmojiButton
                  emoji={ChevronRight}
                  onClick={handleNext}
                  isDisabled={regenIndex === draftMessageRegens.length - 1}
                />
              </MessageInlineEmojiRow>
            </>
            <BaseMessageEmojiButton emoji={RotateCcw} onClick={handleRetry} />
          </Flex>
        ) : undefined
      }
    />
  );
};
