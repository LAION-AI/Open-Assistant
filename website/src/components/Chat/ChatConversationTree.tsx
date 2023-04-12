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

export const ChatConversationTree = memo(function ChatConversationTree({
  messages,
  ...props
}: ChatConversationTreeProps) {
  const tree = useMemo(() => buildTree(messages), [messages]);
  if (!tree) return null;

  return (
    <>
      <ChatMessageEntry message={tree} {...props}></ChatMessageEntry>
      {tree.children.length > 0 && <TreeChildren trees={tree.children} {...props} />}
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

  const node = (
    <ChatMessageEntry
      message={currentTree}
      {...props}
      canRetry={currentTree.children.length === 0}
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

  if (retryingParentId !== null && trees.findIndex((t) => t.parent_id === retryingParentId) !== -1) {
    if (trees[0].role === "prompter") {
      return node;
    }

    return null; // this node is being regenerated, so we skip render
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
