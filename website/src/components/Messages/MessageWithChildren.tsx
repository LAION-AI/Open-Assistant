import { Box, CircularProgress, Stack, StackProps, Text, TextProps, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import { useState } from "react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import fetcher from "src/lib/fetcher";
import useSWR from "swr";

const MessageHeaderProps: TextProps = {
  fontSize: "xl",
  fontWeight: "bold",
  fontFamily: "Inter",
  py: "2",
};

const MessageStackProps: StackProps = {
  spacing: "2",
  alignItems: "start",
  justifyContent: "center",
};

interface MessageWithChildrenProps {
  id: string;
  depth?: number;
  maxDepth?: number;
  isOnlyChild?: boolean;
}

export function MessageWithChildren(props: MessageWithChildrenProps) {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const childBackgroundColor = useColorModeValue("gray.200", "gray.800");

  const { id, depth, maxDepth, isOnlyChild = true } = props;

  const [message, setMessage] = useState(null);
  const [children, setChildren] = useState(null);

  const { isLoading } = useSWR(id ? `/api/messages/${id}` : null, fetcher, {
    onSuccess: (data) => {
      setMessage(data);
    },
    onError: () => {
      setMessage(null);
    },
  });
  const { isLoading: isLoadingChildren } = useSWR(id ? `/api/messages/${id}/children` : null, fetcher, {
    onSuccess: (data) => {
      setChildren(data);
    },
    onError: () => {
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
          <Box pb={isFirstOrOnly ? "4" : "0"}>
            <Text textAlign="left" {...MessageHeaderProps}>
              {isFirst ? "Message" : depth === 1 ? "Children" : "Ancestor"}
            </Text>
            <Box width="fit-content" bg={backgroundColor} padding="4" borderRadius="xl" boxShadow="base">
              <MessageTableEntry item={message} />
            </Box>
          </Box>
        </>
      )}
      {children && Array.isArray(children) && children.length > 0 ? (
        renderRecursive ? (
          <Stack {...MessageStackProps}>
            <Box bg={childBackgroundColor} padding="4" borderRadius="xl">
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
            </Box>
          </Stack>
        ) : (
          <>
            <Text {...MessageHeaderProps}>{isFirstOrOnly ? "Children" : "Ancestor"}</Text>
            <Stack {...MessageStackProps}>
              {children.map((item, idx) => (
                <Box flex="1" key={`recursiveMessageWChildren_${idx}`}>
                  <MessageTableEntry item={item} />
                </Box>
              ))}
            </Stack>
          </>
        )
      ) : (
        <></>
      )}
    </>
  );
}
