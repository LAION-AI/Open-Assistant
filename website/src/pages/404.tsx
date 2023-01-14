import { Center, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { PageEmptyState } from "src/components/EmptyState";
import { getTransparentHeaderLayout } from "src/components/Layout";

function Error() {
  const backgroundColor2 = useColorModeValue("gray.50", "gray.900");

  return (
    <>
      <Head>
        <title>404 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Center bg={backgroundColor2} flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased">
        <PageEmptyState />
      </Center>
    </>
  );
}

Error.getLayout = getTransparentHeaderLayout;
export default Error;
