import { Box, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useState } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { MessageWithChildren } from "src/components/Messages/MessageWithChildren";
import fetcher from "src/lib/fetcher";
import useSWR from "swr";

const MessageDetail = ({ id }) => {
  const backgroundColor = useColorModeValue("white", "gray.700");

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
    return (
      <Box className="w-full">
        <LoadingScreen text="Loading..." />
      </Box>
    );
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
      <Box width="full">
        <Box>
          {parent && (
            <>
              <Box pb="4">
                <Text fontFamily="Inter" fontWeight="bold" fontSize="xl" pb="2">
                  Parent
                </Text>
                <Box bg={backgroundColor} padding="4" borderRadius="xl" boxShadow="base" width="fit-content">
                  {" "}
                  <MessageTableEntry item={parent} idx={1} />
                </Box>
              </Box>
            </>
          )}
        </Box>
        <Box pb="4">
          <MessageWithChildren id={id} maxDepth={2} />
        </Box>
      </Box>
    </>
  );
};

MessageDetail.getInitialProps = async ({ query }) => {
  const { id } = query;
  return { id };
};

MessageDetail.getLayout = (page) => getDashboardLayout(page);
export default MessageDetail;
