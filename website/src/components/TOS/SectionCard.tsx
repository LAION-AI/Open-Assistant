import { Box, Flex, Heading, Stack, Text, useColorModeValue } from "@chakra-ui/react";

import { ChapterInfo, SectionInfo } from "./PolicyContents";

export interface ChapterProps {
  chapter: ChapterInfo;
}

export interface SectionProps {
  section: SectionInfo;
}

export const ChapterCard = ({ chapter }: ChapterProps) => {
  const backgroundColor = useColorModeValue("gray.100", "gray.800");

  return (
    <Box bg={backgroundColor} p="6" borderRadius="xl" shadow="base">
      <Stack spacing="4">
        <Stack>
          <Flex alignItems="end" gap="2">
            <Text as="b" fontSize="xl" color="blue.500">
              {chapter.number}
            </Text>
            <Heading as="h3" size="lg">
              {chapter.title}
            </Heading>
          </Flex>
          <Text>{chapter.desc}</Text>
        </Stack>
        {chapter.sections && chapter.sections.length
          ? chapter.sections.map((section, sectionIndex) => <SectionCard key={sectionIndex} section={section} />)
          : ""}
      </Stack>
    </Box>
  );
};

export const SectionCard = ({ section }: SectionProps) => {
  const backgroundColor = useColorModeValue("gray.200", "gray.700");

  return (
    <Box bg={backgroundColor} p="6" borderRadius="lg">
      <Stack>
        <Flex alignItems="end" gap="2">
          <Text as="b" fontSize="md" color="blue.500">
            {section.number}
          </Text>
          <Heading as="h4" size="md">
            {section.title}
          </Heading>
        </Flex>
        <Text>{section.desc}</Text>
      </Stack>
    </Box>
  );
};
