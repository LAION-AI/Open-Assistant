import {
  Avatar,
  Box,
  Button,
  CircularProgress,
  Collapse,
  Divider,
  Flex,
  Tag,
  useColorModeValue,
} from "@chakra-ui/react";
import { lazy, useEffect, useState, useCallback } from "react";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

import { BaseMessageEmojiButton } from "../Messages/MessageEmojiButton";
import { InferenceMessage } from "src/types/Chat";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { PluginUsageDetails } from "../Messages/PluginUsageDetails";
import { WorkParametersDisplay } from "./WorkParameters";
const RenderedMarkdown = lazy(() => import("../Messages/RenderedMarkdown"));

type OnDraftPickedFn = (chat_id: string, regen_index: number, message_index: number) => void;
type OnRetryFn = (params: { parentId: string; chatId: string }) => void;

type ChatAssistantDraftViewerProps = {
  chatId: string;
  streamedDrafts: string[];
  draftMessages: InferenceMessage[][];
  onDraftPicked: OnDraftPickedFn;
  onRetry: OnRetryFn;
};

export const ChatAssistantDraftViewer = ({
  chatId,
  streamedDrafts,
  draftMessages,
  onDraftPicked,
  onRetry,
}: ChatAssistantDraftViewerProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [expandedMessage, setExpandedMessage] = useState<number>(0);
  const [regenIndex, setRegenIndex] = useState<number>(0);

  useEffect(() => {
    const areAllMessagesEmpty = streamedDrafts.every((message) => message === "");
    setIsLoading(areAllMessagesEmpty);
  }, [streamedDrafts, setIsLoading]);

  useEffect(() => {
    const areAllMessagesComplete =
      regenIndex < draftMessages.length &&
      draftMessages[regenIndex]?.length !== 0 &&
      draftMessages[regenIndex].every((message) =>
        ["complete", "aborted_by_worker", "cancelled", "timeout"].includes(message.state)
      );
    setIsComplete(areAllMessagesComplete);
  }, [regenIndex, draftMessages, setIsComplete]);

  const handlePrevious = useCallback(() => {
    setRegenIndex(regenIndex > 0 ? regenIndex - 1 : regenIndex);
  }, [setRegenIndex, regenIndex]);

  const handleNext = useCallback(() => {
    setRegenIndex(regenIndex < draftMessages.length - 1 ? regenIndex + 1 : regenIndex);
  }, [setRegenIndex, regenIndex, draftMessages]);

  useEffect(() => {
    if (!draftMessages || draftMessages.length === 0) {
      setRegenIndex(0);
    }
  }, [draftMessages, setRegenIndex]);

  const handleToggleExpand = (index) => {
    setExpandedMessage(index === expandedMessage ? -1 : index);
  };

  const handleRetry = useCallback(() => {
    if (onRetry && regenIndex < draftMessages.length && draftMessages[regenIndex]?.length !== 0) {
      setExpandedMessage(0);
      onRetry({ parentId: draftMessages[regenIndex][0].parent_id, chatId: draftMessages[regenIndex][0].chat_id });
      setRegenIndex(draftMessages.length);
    }
  }, [onRetry, regenIndex, draftMessages, setExpandedMessage, setRegenIndex]);

  const containerBackgroundColor = useColorModeValue("#DFE8F1", "#42536B");
  const responseHoverBackgroundColor = useColorModeValue("gray.300", "blackAlpha.300");

  return (
    <Flex
      key="chat-message-select"
      width="full"
      gap={0.5}
      flexDirection={{ base: "column", md: "row" }}
      alignItems="start"
      position="relative"
      padding={{ base: 3, md: 0 }}
      background={{ base: containerBackgroundColor, md: "transparent" }}
      borderRadius={{ base: "18px", md: 0 }}
      maxWidth={{ base: "3xl", "2xl": "4xl" }}
    >
      <Avatar
        size={{ base: "xs", md: "sm" }}
        marginRight={{ base: 0, md: 2 }}
        marginTop={{ base: 0, md: `6px` }}
        marginBottom={{ base: 1.5, md: 0 }}
        borderColor={"blackAlpha.200"}
        _dark={{ backgroundColor: "blackAlpha.300" }}
        src="/images/logos/logo.png"
      />
      <Flex
        background={containerBackgroundColor}
        borderRadius={{ base: 0, md: "18px" }}
        gap={1}
        width={isLoading ? "fit-content" : "full"}
        padding={{ base: 0, md: 4 }}
        flexDirection="column"
      >
        {isLoading ? (
          <CircularProgress isIndeterminate />
        ) : (
          <>
            {(isComplete && regenIndex < draftMessages.length && draftMessages[regenIndex]?.length !== 0
              ? draftMessages[regenIndex]
              : streamedDrafts
            ).map((message, index) => (
              <>
                <Box
                  key={`message-${index}`}
                  borderRadius="md"
                  padding={2}
                  gap={2}
                  width={"full"}
                  rounded="md"
                  cursor="pointer"
                  onClick={() => onDraftPicked(chatId, regenIndex, index)}
                  _hover={{ backgroundColor: responseHoverBackgroundColor }}
                  transition="background-color 0.2 ease-in-out"
                >
                  <Tag size="md" variant="outline" maxW="max-content" marginBottom={1.5} borderRadius="full">
                    Draft {index + 1}
                  </Tag>
                  <Collapse startingHeight={100} in={expandedMessage === index}>
                    <Box
                      bgGradient={
                        expandedMessage === index
                          ? "linear(to-b, #000000, #000000)"
                          : "linear(to-b, #000000 40px, #00000000 95px)"
                      }
                      _dark={{
                        bgGradient:
                          expandedMessage === index
                            ? "linear(to-b, #FFFFFF, #FFFFFF)"
                            : "linear(to-b, #FFFFFF 40px, #00000000 95px)",
                      }}
                      backgroundClip={"text"}
                      padding={0}
                      minHeight={"100px"}
                      gap={0}
                    >
                      {isComplete ? (
                        <>
                          <PluginUsageDetails usedPlugin={message.usedPlugin} />
                          <RenderedMarkdown markdown={message.content} disallowedElements={[]}></RenderedMarkdown>
                        </>
                      ) : (
                        message
                      )}
                    </Box>
                  </Collapse>
                  <Button
                    size="sm"
                    width={"fit-content"}
                    marginTop="1rem"
                    marginLeft={"auto"}
                    background={"white"}
                    _dark={{
                      background: "gray.500",
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleExpand(index);
                    }}
                  >
                    Show {expandedMessage === index ? "Less" : "More"}
                  </Button>
                </Box>
                {index !== streamedDrafts.length - 1 && (
                  <Divider
                    key={`divider-${index}`}
                    marginY="2.0"
                    borderColor="blackAlpha.300"
                    _dark={{
                      borderColor: "blackAlpha.700",
                    }}
                  />
                )}
              </>
            ))}
            {isComplete && (
              <Flex justifyContent={"space-between"}>
                <>
                  <MessageInlineEmojiRow gap="0.5">
                    <BaseMessageEmojiButton
                      emoji={ChevronLeft}
                      onClick={handlePrevious}
                      isDisabled={regenIndex === 0}
                    />
                    <Box fontSize="xs">{`${regenIndex + 1}/${draftMessages.length}`}</Box>
                    <BaseMessageEmojiButton
                      emoji={ChevronRight}
                      onClick={handleNext}
                      isDisabled={regenIndex === draftMessages.length - 1}
                    />
                  </MessageInlineEmojiRow>
                </>
                <BaseMessageEmojiButton emoji={RotateCcw} onClick={handleRetry} />
              </Flex>
            )}
            {isComplete &&
              regenIndex < draftMessages.length &&
              draftMessages[regenIndex]?.length !== 0 &&
              draftMessages[regenIndex][0]?.work_parameters && (
                <WorkParametersDisplay parameters={draftMessages[regenIndex][0].work_parameters} />
              )}
          </>
        )}
      </Flex>
    </Flex>
  );
};
