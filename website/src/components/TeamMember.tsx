import { Avatar, Badge, Box, Flex, Text, useColorModeValue } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Link from "next/link";

export interface TeamMemberProps {
  name: string;
  imageURL: string;
  githubURL?: string;
  title: string;
}
export function TeamMember({ name, imageURL, githubURL, title }: TeamMemberProps) {
  const contributorBackgroundColor = useColorModeValue("gray.200", "gray.700");
  return (
    <Flex gap="1" bg={contributorBackgroundColor} borderRadius="md" p="2">
      <Avatar src={imageURL} loading="lazy" name={name} />
      <Box ml="3">
        <Text fontWeight="bold">
          {name}
          {githubURL && (
            <Badge ml="2" mb="0.5">
              <Link href={githubURL} target="_default" rel="noreferrer" title="github">
                <Github size={12} />
              </Link>
            </Badge>
          )}
        </Text>
        <Text fontSize="sm">{title}</Text>
      </Box>
    </Flex>
  );
}
