import { Box, Container, Text, HStack, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { colors } from "styles/Theme/colors";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";

const MessageDetail = () => {
  const bg = useColorModeValue("white", colors.dark.bg);
  const router = useRouter()
  const { id } = router.query

  /** State arrays of messages */
  const [message, setMessage] = useState(null);
  const [parent, setParent] = useState(null);
  const [children, setChildren] = useState(null);

  /** Fetching functions */
  const { isLoading } = useSWRImmutable(id ? `/api/messages/${id}` : null, fetcher, {
    onSuccess: (data) => {
      setMessage(data);
    },
    onError: (err, key, config) => {
      setMessage(null);
    },
  });
  const { isLoading: isLoadingChildren } = useSWRImmutable(id ? `/api/messages/${id}/children` : null, fetcher, {
    onSuccess: (data) => {
      setChildren(data);
    },
    onError: (err, key, config) => {
      setChildren(null);
    },
  });
  const { isLoading: isLoadingParent } = useSWRImmutable(id ? `/api/messages/${id}/parent` : null, fetcher, {
    onSuccess: (data) => {
      setParent(data);
    },
    onError: (err, key, config) => {
      setParent(null);
    },
  });

  if (isLoading || isLoadingChildren || isLoadingParent) {
    return <LoadingScreen text="Loading..." />;
  }
  return <>
    <Head>
      <title>Open Assistant</title>
      <meta
        name="description"
        content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
      />
    </Head>
    <main>
      <Container w='100%'>
        {parent &&
        <>
        <Text align="center" fontSize='xl' pt="4">Parent</Text>
          <Box my="3" bg={bg} rounded='lg' pb="4" px="4">
            <MessageTableEntry item={parent} idx={1} />
          </Box>
          </>
        }
        {message &&
        <>
        <Text align="center" fontSize='xl'>Message</Text>
          <Box my="3" bg={bg} rounded='lg'pb="4" px="4">
            <MessageTableEntry item={message} idx={1} />
          </Box>
          </>
        }
      </Container>
      {children && Array.isArray(children) && children.length > 0 &&
      <>
      <Text align="center" fontSize='xl'>Children</Text>
        <HStack spacing={8} alignItems="start" justifyContent="center">
          {children.map((item, idx) =>
          <Box maxWidth="container.sm" flex="1" px="6" key={idx} >
            <Box my="3" bg={bg} rounded='lg' pb="4" px="6" >
              <MessageTableEntry item={item} idx={idx * 2} />
            </Box>
          </Box>
          )}
        </HStack>
        </>
      }
    </main>
  </>
}

export default MessageDetail;