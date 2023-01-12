import { Box, Heading, Stack } from "@chakra-ui/react";
import Head from "next/head";
import { getTransparentHeaderLayout } from "src/components/Layout";
import { TermsData } from "src/components/TOS/PolicyContents";
import { ChapterCard } from "src/components/TOS/SectionCard";

const TermsOfService = () => {
  return (
    <>
      <Head>
        <title>Terms of Service - Open Assistant</title>
        <meta name="description" content="Open Assistant's Terms of Service" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme max-w-4xl mx-auto">
        <Heading as="h1" size="xl" color="blue.500" mb="6">
          Terms of Service
        </Heading>

        <Stack spacing="8">
          {TermsData.map((chapter, chapterIndex) => (
            <ChapterCard key={chapterIndex} chapter={chapter} />
          ))}
        </Stack>
      </Box>
    </>
  );
};

TermsOfService.getLayout = getTransparentHeaderLayout;

export default TermsOfService;
