import { Avatar, HStack, LinkBox, useColorModeValue } from "@chakra-ui/react";
import { boolean } from "boolean";
import NextLink from "next/link";
import { FlaggableElement } from "src/components/FlaggableElement";
import type { ValidLabel } from "src/types/Task";

interface Message {
  text: string;
  id: string;
  is_assistant: boolean;
}
interface MessageTableEntryProps {
  item: Message;
  idx: number;
  valid_labels: ValidLabel[];
}
export function MessageTableEntry(props: MessageTableEntryProps) {
  const { item, idx, valid_labels } = props;
  const bgColor = useColorModeValue(idx % 2 === 0 ? "bg-slate-800" : "bg-black", "bg-sky-900");

  return (
    <FlaggableElement text={item.text} post_id={item.id} key={`flag_${item.id}`} flaggable_labels={valid_labels}>
      <HStack>
        <Avatar
          name={`${boolean(item.is_assistant) ? "Assitant" : "User"}`}
          src={`${boolean(item.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
        />
        <LinkBox className={`p-4 rounded-md text-white whitespace-pre-wrap ${bgColor} text-white w-full`}>
          <NextLink href={`/messages/${item.id}`} passHref>
            {item.text}
          </NextLink>
        </LinkBox>
      </HStack>
    </FlaggableElement>
  );
}
