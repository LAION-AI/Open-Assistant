import { Box, Button, Center, Link, Text, useColorMode } from "@chakra-ui/react";
import { AlertTriangle } from "lucide-react";
import Head from "next/head";
import { EmptyState } from "src/components/EmptyState";
import { getTransparentHeaderLayout } from "src/components/Layout";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

function ServerError() {
  const { colorMode } = useColorMode();
  const backgroundColor = colorMode === "light" ? "white" : "gray.700";
  const titleColor = colorMode === "light" ? "blue.500" : "blue.300";
  return (
    <>
      <Head>
        <title>500 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Center flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased oa-basic-theme">
        <EmptyState text="Sorry, we encountered a server error. We're not sure what went wrong." icon={AlertTriangle} />
        <Box display="flex" flexDirection="column" alignItems="center" gap="2" mt="6">
          <Text fontSize="sm">If you were trying to contribute data but ended up here, please file a bug.</Text>
          <Button
            width="fit-content"
            leftIcon={<AlertTriangle size="1em" color={titleColor} aria-hidden="true" />}
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
