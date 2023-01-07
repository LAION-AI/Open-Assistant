import { Box, CircularProgress, Flex, HStack, StackDivider, Text, TextProps, StackProps } from "@chakra-ui/react";
import { useState } from "react";
import useSWR from "swr";

import fetcher from "src/lib/fetcher";
import { MessageTableEntry } from "./MessageTableEntry";
import { boolean } from "boolean";

const MessageHeaderProps: TextProps = {
  align: "center",
  fontSize: "xl",
  py: "2",
};

const MessageStackProps: StackProps = {
  spacing: "2",
  alignItems: "start",
  justifyContent: "center",
  divider: <StackDivider />,
};

interface MessageWithChildrenProps {
  id: string;
  depth?: number;
  maxDepth?: number;
  isOnlyChild?: boolean;
}

export function MessageWithChildren(props: MessageWithChildrenProps) {
  const { id, depth, maxDepth, isOnlyChild = true } = props;

  const [message, setMessage] = useState(null);
  const [children, setChildren] = useState(null);

  const { isLoading } = useSWR(id ? `/api/messages/${id}` : null, fetcher, {
    onSuccess: (data) => {
      setMessage(data);
    },
    onError: (err, key, config) => {
      setMessage(null);
    },
  });
  const { isLoading: isLoadingChildren } = useSWR(id ? `/api/messages/${id}/children` : null, fetcher, {
    onSuccess: (data) => {
      setChildren(data);
    },
    onError: (err, key, config) => {
      setChildren(null);
    },
  });

  const renderRecursive = maxDepth && ((depth && depth < maxDepth) || !depth);
  const isFirst = depth === 0 || !depth;
  const isFirstOrOnly = isFirst || boolean(isOnlyChild);

  if (isLoading || isLoadingChildren) {
    return <CircularProgress isIndeterminate />;
  }

  return (
    <>
      {message && (
        <>
          <Text {...MessageHeaderProps}>{isFirst ? "Message" : depth === 1 ? "Children" : "Ancestor"}</Text>
          <Flex justifyContent="center" pb="2">
            <Box maxWidth="container.sm" flex="1" px={isFirstOrOnly ? [4, 6, 8, 9] : "0"}>
              <Box px={isFirstOrOnly ? "2" : "0"}>
                <MessageTableEntry item={message} idx={1} />
              </Box>
            </Box>
          </Flex>
        </>
      )}
      {children && Array.isArray(children) && children.length > 0 ? (
        renderRecursive ? (
          <HStack {...MessageStackProps}>
            {children.map((item, idx) => (
              <Box flex="1" key={`recursiveMessageWChildren_${idx}`}>
                <MessageWithChildren
                  id={item.id}
                  depth={depth ? depth + 1 : 1}
                  maxDepth={maxDepth}
                  isOnlyChild={children.length === 1 && isOnlyChild}
                />
              </Box>
            ))}
          </HStack>
        ) : (
          <>
            <Text {...MessageHeaderProps}>{isFirstOrOnly ? "Children" : "Ancestor"}</Text>
            <HStack {...MessageStackProps}>
              {children.map((item, idx) => (
                <Box maxWidth="container.sm" flex="1" key={`recursiveMessageWChildren_${idx}`}>
                  <MessageTableEntry item={item} idx={idx * 2} />
                </Box>
              ))}
            </HStack>
          </>
        )
      ) : (
        <></>
      )}
    </>
  );
}
