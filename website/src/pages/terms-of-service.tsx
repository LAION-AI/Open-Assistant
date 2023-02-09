import { Box, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { getTransparentHeaderLayout } from "src/components/Layout";
import { TermsOfService } from "src/components/ToS";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const TermsOfServicePage = () => {
  return (
    <>
      <Head>
        <title>Terms of Service - Open Assistant</title>
        <meta name="description" content="Open Assistant's Terms of Service" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme">
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

TermsOfServicePage.getLayout = getTransparentHeaderLayout;

export default TermsOfServicePage;
