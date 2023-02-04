import { Box, Flex, Heading, Stack, Text, useColorModeValue } from "@chakra-ui/react";

export interface ChapterInfo {
  number: string;
  title: string;
  desc: string;
}

export interface ChapterProps {
  chapter: ChapterInfo;
  children: React.ReactNode;
}

export const PolicyChapterCard = ({ chapter, children }: ChapterProps) => {
  const backgroundColor = useColorModeValue("gray.100", "gray.800");

  return (
    <Box bg={backgroundColor} p="6" borderRadius="xl" shadow="base">
      <Stack spacing="4">
        <Stack>
          <Flex alignItems="end" gap="2">
            <Text as="b" fontSize="md" color="blue.500">
              {chapter.number}
            </Text>
            <Heading as="h3" size="md">
              {chapter.title}
            </Heading>
          </Flex>
          <Text>{chapter.desc}</Text>
        </Stack>
        {children}
      </Stack>
    </Box>
  );
};
