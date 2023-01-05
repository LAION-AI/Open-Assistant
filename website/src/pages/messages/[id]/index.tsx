import { Box, Container, Flex, HStack, useColorModeValue } from "@chakra-ui/react";
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
  const [message, setMessage] = useState(null);
  const [parent, setParent]= useState(null);
  const [children, setChildren] = useState(null);

  const { isLoading } = useSWRImmutable(`/api/messages/${id}`, fetcher, {
    onSuccess: (data) => {
      setMessage(data);
    },
  });

  const { isLoading: isLoadingChildren } = useSWRImmutable(`/api/messages/${id}/children`, fetcher, {
    onSuccess: (data) => {
      setChildren(data);
    },
  });

  const { isLoading: isLoadingParent } = useSWRImmutable(`/api/messages/${id}/parent`, fetcher, {

    onSuccess: (data) => {
      console.log(data);
      setParent(data);
    },
    onError: (err, key, config) => {
      console.log(parent);
    }
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
      <Container>
      {parent && 
        <Box my="3" bg={bg} rounded='lg' p="4">
            <MessageTableEntry item={parent} idx={1} />
          </Box>
        }
        {message &&
          <Box my="3" bg={bg} rounded='lg' p="4">
            <MessageTableEntry item={message} idx={1} />
          </Box>
        }
          </Container>
          {children && Array.isArray(children) &&
          <HStack spacing={8} alignItems="start">
            {children.map((item, idx) =>
              <Box bg={bg} rounded='lg' flex="1" p="4">
                <MessageTableEntry item={item} idx={idx * 2} />
              </Box>
          )}
          </HStack>
          }
    </main>
  </>
}

export default MessageDetail;