import { Avatar, Badge, Box, Flex, FlexProps, Text, useColorModeValue } from "@chakra-ui/react";
import { Github } from "@icons-pack/react-simple-icons";
import Link from "next/link";

export interface TeamMemberProps {
  name: string;
  imageURL: string;
  url?: string;
  githubURL?: string;
  title: string;
  rootProps?: FlexProps;
}

export function TeamMember({ name, url, imageURL, githubURL, title, rootProps }: TeamMemberProps) {
  const contributorBackgroundColor = useColorModeValue("gray.200", "gray.700");
  return (
    <Flex gap="3" bg={contributorBackgroundColor} borderRadius="md" p="2" {...rootProps}>
      <Avatar src={imageURL} loading="lazy" name={name} />
      <Box>
        <Flex gap={3} fontWeight="bold">
          {url ? (
            <Link href={url} className="underline">
              {name}
            </Link>
          ) : (
            <Text>{name}</Text>
          )}
          {githubURL && (
            <Link href={githubURL} target="_default" rel="noreferrer" title="github">
              <Badge mb="1">
                <Github size={12} />
              </Badge>
            </Link>
          )}
        </Flex>
        <Text fontSize="sm">{title}</Text>
      </Box>
    </Flex>
  );
}
