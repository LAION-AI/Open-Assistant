import { Box, Flex, Heading, Stack, Text, useColorModeValue } from "@chakra-ui/react";

export interface SectionInfo {
  number: string;
  title: string;
  desc: string;
}

export interface SectionProps {
  section: SectionInfo;
}

export const PolicySectionCard = ({ section }: SectionProps) => {
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
