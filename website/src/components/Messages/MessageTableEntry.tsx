import { Avatar, HStack, LinkBox, LinkOverlay, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import { FlaggableElement } from "src/components/FlaggableElement";

interface Message {
  text: string;
  id: string;
  is_assistant: boolean;
}
interface MessageTableEntryProps {
  item: Message;
}
export function MessageTableEntry(props: MessageTableEntryProps) {
  const { item } = props;
  const backgroundColor = useColorModeValue("gray.50", "gray.800");

  return (
    <div>
      <FlaggableElement text={item.text} message_id={item.message_id} post_id={item.id} key={`flag_${item.id}`}>
        <HStack>
          <Avatar
            size="sm"
            name={`${boolean(item.is_assistant) ? "Assistant" : "User"}`}
            src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          />

          <LinkBox bg={backgroundColor} fontFamily="Inter" className={`p-4 rounded-md whitespace-pre-wrap w-full`}>
            <LinkOverlay href={`/messages/${item.id}`}>{item.text}</LinkOverlay>
          </LinkBox>
        </HStack>
      </FlaggableElement>
    </div>
  );
}
