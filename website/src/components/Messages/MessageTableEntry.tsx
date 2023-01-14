import { Avatar, Box, HStack, LinkBox, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import Link from "next/link";
import { FlaggableElement } from "src/components/FlaggableElement";
import { Message } from "src/types/Conversation";

interface MessageTableEntryProps {
  item: Message;
  enabled?: boolean;
}

export function MessageTableEntry(props: MessageTableEntryProps) {
  const { item } = props;
  const backgroundColor = useColorModeValue("gray.100", "gray.700");
  const backgroundColor2 = useColorModeValue("#DFE8F1", "#42536B");

  const avatarColor = useColorModeValue("white", "black");
  const borderColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");

  return (
    <FlaggableElement message={item}>
      <HStack w="100%" gap={2}>
        <Box borderRadius="full" border="solid" borderWidth="1px" borderColor={borderColor} bg={avatarColor}>
          <Avatar
            size="sm"
            name={`${boolean(item.is_assistant) ? "Assistant" : "User"}`}
            src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          />
        </Box>
        {props.enabled ? (
          <Box maxWidth="xl">
            <Link href={`/messages/${item.id}`}>
              <LinkBox
                bg={item.is_assistant ? backgroundColor : backgroundColor2}
                className={`p-4 rounded-md whitespace-pre-wrap w-full`}
              >
                {item.text}
              </LinkBox>
            </Link>
          </Box>
        ) : (
          <Box
            maxWidth="xl"
            bg={item.is_assistant ? backgroundColor : backgroundColor2}
            className={`p-4 rounded-md whitespace-pre-wrap w-full`}
          >
            {item.text}
          </Box>
        )}
      </HStack>
    </FlaggableElement>
  );
}
