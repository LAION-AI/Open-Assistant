import { Box, Button, Center, Link, Text } from "@chakra-ui/react";
import Head from "next/head";
import { FiAlertTriangle } from "react-icons/fi";
import { EmptyState } from "src/components/EmptyState";
import { getTransparentHeaderLayout } from "src/components/Layout";

function ServerError() {
  return (
    <>
      <Head>
        <title>500 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Center flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased">
        <EmptyState
          text="Sorry, we encountered a server error. We're not sure what went wrong."
          icon={FiAlertTriangle}
        />
        <Box display="flex" flexDirection="column" alignItems="center" gap="2" mt="6">
          <Text fontSize="sm">If you were trying to contribute data but ended up here, please file a bug.</Text>
          <Button
            width="fit-content"
            leftIcon={<FiAlertTriangle className="text-blue-500" aria-hidden="true" />}
            variant="solid"
            size="xs"
          >
            <Link
              key="Report a Bug"
              href="https://github.com/LAION-AI/Open-Assistant/issues/new/choose"
              aria-label="Report a Bug"
              className="flex items-center"
              _hover={{ textDecoration: "none" }}
              isExternal
            >
              Report a Bug
            </Link>
          </Button>
        </Box>
      </Center>
    </>
  );
}

ServerError.getLayout = getTransparentHeaderLayout;

export default ServerError;
