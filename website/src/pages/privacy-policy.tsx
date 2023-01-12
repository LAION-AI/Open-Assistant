import { Box, Heading, Link, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { getTransparentHeaderLayout } from "src/components/Layout";
import { PrivacyPolicyData } from "src/components/TOS/PolicyContents";
import { ChapterCard } from "src/components/TOS/SectionCard";

const PrivacyPolicy = () => {
  const backgroundColor = useColorModeValue("gray.100", "gray.800");

  return (
    <>
      <Head>
        <title>Privacy Policy - Open Assistant</title>
        <meta name="description" content="Open Assistant's Privacy Policy" />
      </Head>
      <Box fontFamily="Inter" p="6" className="oa-basic-theme">
        <Box className="max-w-4xl mx-auto">
          <Stack spacing="6" mb="6">
            <Heading as="h1" size="xl" color="blue.500">
              Privacy Policy
            </Heading>

            <Box bg={backgroundColor} p="6" pt="4" borderRadius="xl" shadow="base">
              <Stack>
                <Heading as="h3" size="lg">
                  Overview
                </Heading>
                <Text>
                  We are pleased that you are interested in our work and welcome you to our website laion.ai. In this
                  Privacy Policy you will learn which personal data we process when you visit our website and to what
                  kind of purpose, and also what rights you have regarding these data. Categorically, we only store data
                  as long as we need them. There is no legal obligation to provide us with personal data. Automated
                  decision-making, as per Article 22 of the EU-GDPR, will not happen.
                </Text>
              </Stack>
            </Box>
          </Stack>

          <Stack spacing="8">
            {PrivacyPolicyData.map((chapter, chapterIndex) => (
              <ChapterCard key={chapterIndex} chapter={chapter} />
            ))}
          </Stack>

          <Box bg={backgroundColor} p="6" pt="4" mt="8" borderRadius="xl" shadow="base">
            <Stack>
              <Heading as="h3" size="lg">
                Submitting Requests
              </Heading>
              <Text>
                Email:{" "}
                <Link href="mailto:privacy@open-assistant.io" color="blue.500" fontWeight="bold">
                  privacy@open-assistant.io
                </Link>
              </Text>
            </Stack>
          </Box>
        </Box>
      </Box>
    </>
  );
};

PrivacyPolicy.getLayout = getTransparentHeaderLayout;

export default PrivacyPolicy;
