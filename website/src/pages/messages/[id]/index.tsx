import { Box, Container, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { MessageWithChildren } from "src/components/Messages/MessageWithChildren";
import fetcher from "src/lib/fetcher";
import useSWR from "swr";

const MessageDetail = ({ id }) => {
  const mainBg = useColorModeValue("bg-slate-300", "bg-slate-900");

  const [parent, setParent] = useState(null);

  const { isLoading: isLoadingParent } = useSWR(id ? `/api/messages/${id}/parent` : null, fetcher, {
    onSuccess: (data) => {
      setParent(data);
    },
    onError: () => {
      setParent(null);
    },
  });

  if (isLoadingParent) {
    return <LoadingScreen text="Loading..." />;
  }
  return (
    <>
      <Head>
        <title>Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <main className={`${mainBg}`}>
        <Container w="100%" pt={[2, 2, 4, 4]}>
          {parent && (
            <>
              <Text align="center" fontSize="xl">
                Parent
              </Text>
              <Box rounded="lg" p="2">
                <MessageTableEntry item={parent} idx={1} />
              </Box>
            </>
          )}
        </Container>
        <Box pb="4" maxW="full" px="2">
          <MessageWithChildren id={id} maxDepth={2} />
        </Box>
      </main>
    </>
  );
};

MessageDetail.getInitialProps = async ({ query }) => {
  const { id } = query;
  return { id };
};

export default MessageDetail;
