import { HStack, StackProps } from "@chakra-ui/react";
import { SyntheticEvent } from "react";

const stopPropagation = (e: SyntheticEvent) => e.stopPropagation();

export const MessageInlineEmojiRow = (props: StackProps) => {
  return <HStack justifyContent="end" alignItems="center" pos="relative" onClick={stopPropagation} {...props}></HStack>;
};
