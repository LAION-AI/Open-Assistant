import { Box } from "@chakra-ui/react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import { InferenceMessage } from "src/types/Chat";
import { buildTree, Tree } from "src/utils/buildTree";
import { StrictOmit } from "ts-essentials";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { BaseMessageEmojiButton } from "../Messages/MessageEmojiButton";
import { MessageInlineEmojiRow } from "../Messages/MessageInlineEmojiRow";
import { ChatMessageEntry, ChatMessageEntryProps } from "./ChatMessageEntry";

type ChatConversationTreeProps = { messages: InferenceMessage[]; retryingParentId: string | null } & StrictOmit<
  ChatMessageEntryProps,
  "message"
>;

export const LAST_ASSISTANT_MESSAGE_ID = "last_assistant_message";

export const ChatConversationTree = memo(function ChatConversationTree({
  messages,
  retryingParentId,
  ...props
}: ChatConversationTreeProps) {
  const tree = useMemo(() => buildTree(messages), [messages]);
  if (!tree) return null;

  return (
    <>
      <ChatMessageEntry message={tree} {...props}></ChatMessageEntry>
      {tree.children.length > 0 && (
        <TreeChildren trees={tree.children} {...props} retryingParentId={retryingParentId} />
      )}
    </>
  );
});

const TreeChildren = ({
  trees,
  retryingParentId,
  ...props
}: { trees: Tree<InferenceMessage>[]; retryingParentId: string | null } & StrictOmit<
  ChatMessageEntryProps,
  "message" | "canRetry"
>) => {
  const [index, setIndex] = useState(trees.length - 1);
  useIsomorphicLayoutEffect(() => {
    setIndex(trees.length - 1); // always show last child
  }, [trees.length]);

  const sortedTrees = useMemo(() => trees.sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at)), [trees]);
  const actualIndex = Math.min(index, trees.length - 1); // index sometimes out of bounds because useIsomorphicLayoutEffect only reset the index on the next render

  const currentTree = sortedTrees[actualIndex];
  const length = trees.length;

  const hasSibling = length > 1;

  const handlePrevious = useCallback(() => {
    setIndex((i) => (i > 0 ? i - 1 : i));
  }, []);
  const handleNext = useCallback(() => {
    setIndex((i) => (i < length - 1 ? i + 1 : i));
  }, [length]);

  const isRegenerating = retryingParentId !== null && trees.findIndex((t) => t.parent_id === retryingParentId) !== -1;

  if (isRegenerating && trees[0].role === "assistant") {
    return null; // this node is being regenerated, so we skip render
  }

  const isLeaf = currentTree.children.length === 0;

  const node = (
    <ChatMessageEntry
      message={currentTree}
      {...props}
      canRetry={isLeaf}
      showEncourageMessage={props.showEncourageMessage && isLeaf}
      // TODO refacor away from this dirty hack
      id={isLeaf && currentTree.role === "assistant" ? LAST_ASSISTANT_MESSAGE_ID : undefined}
      data-id={currentTree.id}
      pagingSlot={
        hasSibling ? (
          <>
            <MessageInlineEmojiRow gap="0.5">
              <BaseMessageEmojiButton
                emoji={ChevronLeft}
                onClick={handlePrevious}
                isDisabled={actualIndex === 0}
              ></BaseMessageEmojiButton>
              <Box fontSize="xs">{`${actualIndex + 1}/${length}`}</Box>
              <BaseMessageEmojiButton
                emoji={ChevronRight}
                onClick={handleNext}
                isDisabled={actualIndex === length - 1}
              ></BaseMessageEmojiButton>
            </MessageInlineEmojiRow>
          </>
        ) : undefined
      }
    ></ChatMessageEntry>
  );

  if (isRegenerating) {
    return node;
  }

  return (
    <>
      {node}
      {currentTree.children.length > 0 && (
        <TreeChildren retryingParentId={retryingParentId} trees={currentTree.children} {...props} />
      )}
    </>
  );
};
