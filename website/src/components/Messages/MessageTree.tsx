import { Box, BoxProps } from "@chakra-ui/react";
import { Fragment, memo } from "react";
import { MessageWithChildren } from "src/types/Conversation";

import { MessageTableEntry } from "./MessageTableEntry";

const connectionColor = "gray.300";
const messagePaddingTop = 16;
const avatarSize = 32;
const avartarMarginTop = 6;
const maxDepth = 100; // this only used for debug UI in mobile
const toPx = (val: number) => `${val}px`;

interface MessageTreeProps {
  tree: MessageWithChildren;
  messageId?: string;
  scrollToHighlighted?: boolean;
}

// eslint-disable-next-line react/display-name
export const MessageTree = memo(({ tree, messageId, scrollToHighlighted }: MessageTreeProps) => {
  const renderChildren = (children: MessageWithChildren[], depth = 1) => {
    const hasSibling = children.length > 1;
    return children.map((child, idx) => {
      const hasChildren = child.children.length > 0;
      const isLastChild = idx === children.length - 1;
      return (
        <Fragment key={child.id}>
          <Box position="relative" className="box2">
            <ConnectionCurveBottom left={{ base: toPx(-8), md: toPx(avatarSize / 2 - 1) }}></ConnectionCurveBottom>
            <Box paddingLeft={{ md: "32px", base: "16px" }} position="relative" className="box3">
              {hasSibling && !isLastChild && <Connection isSibling></Connection>}
              <Box pt={`${messagePaddingTop}px`} position="relative" className="box4">
                {hasChildren && depth < maxDepth && <Connection className="connection1"></Connection>}
                <MessageTableEntry
                  showAuthorBadge
                  scrollToHighlighted={scrollToHighlighted}
                  highlight={child.id === messageId}
                  message={child}
                ></MessageTableEntry>
              </Box>
              {depth < maxDepth && renderChildren(child.children, depth + 1)}
            </Box>
          </Box>
        </Fragment>
      );
    });
  };

  return (
    <>
      <Box position="relative" className="root">
        {tree.children.length > 0 && (
          <>
            <Box
              className="root-connection"
              top={{ base: toPx(0), md: toPx(8) }}
              height={{ base: `calc(100% - ${toPx(8 + avatarSize / 2)})`, md: `calc(100% - 8px)` }}
              position="absolute"
              width="2px"
              bg={connectionColor}
              left={toPx(avatarSize / 2 - 1)}
            ></Box>
            <Box
              display={{ base: "block", md: "none" }}
              position="absolute"
              height={`calc(100% - ${toPx(6 + avatarSize / 2)})`}
              width={`10px`}
              top={toPx(6 + avatarSize / 2)}
              borderTopWidth="2px"
              borderTopLeftRadius="10px"
              left="-8px"
              borderTopStyle="solid"
              borderLeftWidth="2px"
              borderColor={connectionColor}
              className="root-curve"
            ></Box>
          </>
        )}
        <MessageTableEntry
          scrollToHighlighted={scrollToHighlighted}
          showAuthorBadge
          message={tree}
          highlight={tree.id === messageId}
        />
      </Box>
      {renderChildren(tree.children)}
    </>
  );
});

const Connection = ({ className, isSibling = false }: { isSibling?: boolean; className?: string }) => {
  const baseTop = toPx(messagePaddingTop + avatarSize / 2 + 6 - (isSibling ? 10 : 0));
  const mdTop = toPx(messagePaddingTop + avatarSize / 2 - (isSibling ? 6 : 0));
  return (
    <Box
      height={{
        base: `calc(100% - ${baseTop})`,
        md: `calc(100% - ${mdTop})`,
      }}
      position="absolute"
      width="2px"
      bg={connectionColor}
      left={{ base: toPx(-8), md: toPx(avatarSize / 2 - 1) }}
      top={{
        base: baseTop,
        md: mdTop,
      }}
      className={`${className}-${isSibling ? "sibling" : ""}`}
    ></Box>
  );
};

const height = avatarSize / 2 + avartarMarginTop + messagePaddingTop;
const width = avatarSize / 2 + 10;
const ConnectionCurveBottom = ({ left }: { left?: BoxProps["left"] }) => {
  return (
    <Box
      position="absolute"
      height={`calc(${toPx(height)})`}
      width={`${width}px`}
      left={left}
      borderBottomWidth="2px"
      borderBottomLeftRadius="10px"
      borderLeftStyle="solid"
      borderLeftWidth="2px"
      borderColor={connectionColor}
      className="curve"
    ></Box>
  );
};
