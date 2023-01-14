import { Box, Center, Link, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { FiAlertTriangle } from "react-icons/fi";
import { getTransparentHeaderLayout } from "src/components/Layout";

function Error() {
  const router = useRouter();
  const backgroundColor = useColorModeValue("white", "gray.800");

  return (
    <>
      <Head>
        <title>404 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Center flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased">
        <Box bg={backgroundColor} p="10" borderRadius="xl" shadow="base">
          <Box display="flex" flexDirection="column" alignItems="center" gap="8">
            <FiAlertTriangle size="30" color="DarkOrange" />
            <Box display="flex" flexDirection="column" alignItems="center" gap="3">
              <Text>Sorry, the page you are looking for does not exist.</Text>
              <Link onClick={() => router.back()} color="blue.500" textUnderlineOffset="3px">
                <Text>Click here to go back</Text>
              </Link>
            </Box>
          </Box>
        </Box>
      </Center>
    </>
  );
}

Error.getLayout = getTransparentHeaderLayout;

export default Error;
