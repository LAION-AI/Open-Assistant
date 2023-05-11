import { Box, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { TermsOfService } from "src/components/ToS";
export { getStaticProps } from "src/lib/defaultServerSideProps";

const TermsOfServicePage = () => {
  return (
    <>
      <Head>
        <title>Terms of Service - Open Assistant</title>
        <meta name="description" content="Open Assistant's Terms of Service" />
      </Head>
      <Box p="6" className="oa-basic-theme">
        <Box className="max-w-4xl mx-auto">
          <Heading as="h1" size="xl" color="blue.500" mb="6">
            Terms of Service
          </Heading>
          <TermsOfService />
        </Box>
      </Box>
    </>
  );
};

export default TermsOfServicePage;
