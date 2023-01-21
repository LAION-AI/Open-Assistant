import { Avatar, Box, HStack, LinkBox, useBreakpoint, useBreakpointValue, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import Link from "next/link";
import { useRouter } from "next/router";
import { useCallback, useMemo } from "react";
import { FlaggableElement } from "src/components/FlaggableElement";
import { Message } from "src/types/Conversation";

interface MessageTableEntryProps {
  item: Message;
  enabled?: boolean;
}

export function MessageTableEntry(props: MessageTableEntryProps) {
  const router = useRouter();

  const { item } = props;

  const goToMessage = useCallback(() => router.push(`/messages/${item.id}`), [router, item.id]);

  const backgroundColor = useColorModeValue("gray.100", "gray.700");
  const backgroundColor2 = useColorModeValue("#DFE8F1", "#42536B");

  const borderColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");

  const inlineAvatar = useBreakpointValue({ base: true, sm: false });

  const avatar = useMemo(
    () => (
      <Avatar
        borderColor={borderColor}
        size={inlineAvatar ? "xs" : "sm"}
        mr={inlineAvatar ? 2 : 0}
        name={`${boolean(item.is_assistant) ? "Assistant" : "User"}`}
        src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
      />
    ),
    [borderColor, inlineAvatar, item.is_assistant]
  );

  return (
    <FlaggableElement message={item}>
      <HStack w={["full", "full", "full", "fit-content"]} gap={2}>
        {!inlineAvatar && avatar}
        <Box
          width={["full", "full", "full", "fit-content"]}
          maxWidth={["full", "full", "full", "2xl"]}
          p="4"
          borderRadius="md"
          bg={item.is_assistant ? backgroundColor : backgroundColor2}
          onClick={props.enabled && goToMessage}
          _hover={props.enabled && { cursor: "pointer", opacity: 0.9 }}
          whiteSpace="pre-wrap"
        >
          {inlineAvatar && avatar}
          {item.text}
        </Box>
      </HStack>
    </FlaggableElement>
  );
}
