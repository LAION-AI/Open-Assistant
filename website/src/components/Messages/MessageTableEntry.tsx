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
  const backgroundColor = useColorModeValue("gray.50", "gray.800");

  return (
    <div>
      <FlaggableElement message={item} key={`flag_${item.id || item.frontend_message_id}`}>
        <HStack>
          <Avatar
            size="sm"
            name={`${boolean(item.is_assistant) ? "Assistant" : "User"}`}
            src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          />

          {props.enabled ? (
            <Link href={`/messages/${item.id}`}>
              <LinkBox bg={backgroundColor} className={`p-4 rounded-md whitespace-pre-wrap w-full`}>
                {item.text}
              </LinkBox>
            </Link>
          ) : (
            <Box bg={backgroundColor} className={`p-4 rounded-md whitespace-pre-wrap w-full`}>
              {item.text}
            </Box>
          )}
        </HStack>
      </FlaggableElement>
    </div>
  );
}
