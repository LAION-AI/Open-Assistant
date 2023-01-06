import { Box, CircularProgress, Flex, HStack, Text } from "@chakra-ui/react";
import { useState } from "react";
import useSWR from "swr";

import fetcher from "src/lib/fetcher";
import { MessageTableEntry } from "./MessageTableEntry";

interface MessageWithChildrenProps {
  id: string;
  depth?: number;
  maxDepth?: number;
}

export function MessageWithChildren(props: MessageWithChildrenProps) {
  const { id, depth, maxDepth } = props;

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

  if (isLoading || isLoadingChildren) {
    return <CircularProgress isIndeterminate />;
  }

  return (
    <>
      {message && (
        <>
          <Text align="center" fontSize="xl">
            {depth === 0 || !depth ? "Message" : depth === 1 ? "Children" : "Ancestor"}
          </Text>
          <Flex justifyContent="center">
            <Box maxWidth="container.sm" flex="1" px={[4, 6, 8, 9]}>
              <Box rounded="lg" p="2">
                <MessageTableEntry item={message} idx={1} />
              </Box>
            </Box>
          </Flex>
        </>
      )}
      {children && Array.isArray(children) && children.length > 0 ? (
        renderRecursive ? (
          <HStack spacing={8} alignItems="start" justifyContent="center">
            {children.map((item, idx) => (
              <Box flex="1" key={`recursiveMessageWChildren_${idx}`}>
                <MessageWithChildren id={item.id} depth={depth ? depth + 1 : 1} maxDepth={maxDepth} />
              </Box>
            ))}
          </HStack>
        ) : (
          <>
            <Text align="center" fontSize="xl">
              {depth === 0 || !depth ? "Children" : "Ancestor"}
            </Text>
            <HStack spacing={8} alignItems="start" justifyContent="center">
              {children.map((item, idx) => (
                <Box maxWidth="container.sm" flex="1" px={[4, 6, 8, 9]} key={idx}>
                  <Box rounded="lg" p="2">
                    <MessageTableEntry item={item} idx={idx * 2} />
                  </Box>
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
