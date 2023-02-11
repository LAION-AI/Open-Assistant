import { Box } from "@chakra-ui/react";
import { Fragment } from "react";
import { MessageWithChildren } from "src/types/Conversation";

import { MessageTableEntry } from "./MessageTableEntry";

const connectionColor = "gray.300";
const messagePaddingTop = 16;
const avatarSize = 32;
const avartarMarginTop = 6;
const maxDepth = 100; // this only used for debug UI in mobile
const left = avatarSize / 2 - 1;

export const MessageTree = ({ tree, messageId }: { tree: MessageWithChildren; messageId?: string }) => {
  const renderChildren = (children: MessageWithChildren[], depth = 1) => {
    const hasSibling = children.length > 1;
    return children.map((child, idx) => {
      const hasChildren = child.children.length > 0;
      const isLastChild = idx === children.length - 1;
      return (
        <Fragment key={child.id}>
          <Box position="relative" className="box2">
            <ConnectionCurve></ConnectionCurve>
            <Box paddingLeft={`32px`} position="relative" className="box3">
              {hasSibling && !isLastChild && (
                <Box
                  height={`calc(100% - 26px)`}
                  position="absolute"
                  width="2px"
                  bg="gray.300"
                  left={`${left}px`}
                  top="26px"
                ></Box>
              )}
              <Box pt={`${messagePaddingTop}px`} position="relative" className="box4">
                {hasChildren && depth < maxDepth && <Connection className="connection1"></Connection>}
                <MessageTableEntry
                  avartarProps={{
                    mt: `${avartarMarginTop}px`,
                  }}
                  avartarPosition="top"
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
      <Box position="relative">
        <Box height="full" position="absolute" width="2px" bg={connectionColor} left={`${left}px`}></Box>
        <MessageTableEntry
          message={tree}
          avartarPosition="top"
          highlight={tree.id === messageId}
          avartarProps={{
            size: "sm",
          }}
        ></MessageTableEntry>
      </Box>
      {renderChildren(tree.children)}
    </>
  );
};

const Connection = ({ className, isSibling = false }: { isSibling?: boolean; className?: string }) => {
  const top = isSibling ? `26px` : `32px`;
  return (
    <Box
      height={`calc(100% - ${top})`}
      position="absolute"
      width="2px"
      bg="gray.300"
      left={`${left}px`}
      top={top}
      className={className}
    ></Box>
  );
};

const height = avatarSize / 2 + avartarMarginTop + messagePaddingTop;
const width = avatarSize / 2 + 10;
const ConnectionCurve = () => {
  return (
    <Box
      position="absolute"
      height={`${height}px`}
      width={`${width}px`}
      left={`${left}px `}
      borderBottomWidth="2px"
      borderBottomLeftRadius="10px"
      borderLeftStyle="solid"
      borderLeftWidth="2px"
      borderColor={connectionColor}
      className="curve"
    ></Box>
  );
};
