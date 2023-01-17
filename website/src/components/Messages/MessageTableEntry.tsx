import { Avatar, Box, HStack, LinkBox, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import Link from "next/link";
import { useRouter } from "next/router";
import { FlaggableElement } from "src/components/FlaggableElement";
import { Message } from "src/types/Conversation";

interface MessageTableEntryProps {
  item: Message;
  enabled?: boolean;
}

export function MessageTableEntry(props: MessageTableEntryProps) {
  const { item } = props;
  const router = useRouter();
  const { id } = router.query;
  const backgroundColor = useColorModeValue("gray.100", "gray.700");
  const backgroundColor2 = useColorModeValue("#DFE8F1", "#42536B");
  const isClickable = props.enabled && !id;
  const avatarColor = useColorModeValue("white", "black");
  const borderColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");

  return (
    <FlaggableElement message={item}>
      <HStack w={["full", "full", "full", "fit-content"]} gap={2}>
        <Box borderRadius="full" border="solid" borderWidth="1px" borderColor={borderColor} bg={avatarColor}>
          <Avatar
            size="sm"
            name={`${boolean(item.is_assistant) ? "Assistant" : "User"}`}
            src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          />
        </Box>
        {isClickable ? (
          <Box width={["full", "full", "full", "fit-content"]} maxWidth={["full", "full", "full", "2xl"]}>
            <Link href={`/messages/${item.id}`}>
              <LinkBox
                bg={item.is_assistant ? backgroundColor : backgroundColor2}
                p="4"
                borderRadius="md"
                className="whitespace-pre-wrap"
              >
                {item.text}
              </LinkBox>
            </Link>
          </Box>
        ) : (
          <Box
            width={["full", "full", "full", "fit-content"]}
            maxWidth={["full", "full", "full", "2xl"]}
            bg={item.is_assistant ? backgroundColor : backgroundColor2}
            p="4"
            borderRadius="md"
            className="whitespace-pre-wrap"
          >
            {item.text}
          </Box>
        )}
      </HStack>
    </FlaggableElement>
  );
}
