import { Box, CircularProgress, Stack, StackProps, Text, TextProps, useColorModeValue } from "@chakra-ui/react";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { get } from "src/lib/api";
import { Message } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

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

export interface MessageWithChildrenProps {
  id: string;
  depth?: number;
  maxDepth: number;
  isOnlyChild?: boolean;
}

export function MessageWithChildren(props: MessageWithChildrenProps) {
  const backgroundColor = useColorModeValue("white", "gray.800");
  const childBackgroundColor = useColorModeValue("gray.200", "gray.700");
  const { id, depth = 0, maxDepth, isOnlyChild = true } = props;

  const { isLoading, data: message } = useSWRImmutable<Message>(`/api/messages/${id}`, get);
  const { isLoading: isLoadingChildren, data: children = [] } = useSWRImmutable<Message[]>(
    `/api/messages/${id}/children`,
    get
  );

  const renderRecursive = depth < maxDepth || depth === 0;
  const isFirst = depth === 0;
  const isFirstOrOnly = isFirst || !!isOnlyChild;

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
              <MessageTableEntry enabled message={message} />
            </Box>
          </Box>
        </>
      )}
      {children.length > 0 &&
        (renderRecursive ? (
          <Stack {...MessageStackProps}>
            <Box bg={childBackgroundColor} padding="4" borderRadius="xl">
              {children.map((item) => (
                <Box flex="1" key={`recursiveMessageWChildren_${item.id}`}>
                  <MessageWithChildren
                    id={item.id}
                    depth={depth + 1}
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
              <Box
                bg={backgroundColor}
                padding="4"
                borderRadius="xl"
                display="flex"
                flexDirection="column"
                gap="4"
                shadow="base"
              >
                {children.map((message, idx) => (
                  <Box flex="1" key={`recursiveMessageWChildren_${idx}`}>
                    <MessageTableEntry enabled message={message} />
                  </Box>
                ))}
              </Box>
            </Stack>
          </>
        ))}
    </>
  );
}
