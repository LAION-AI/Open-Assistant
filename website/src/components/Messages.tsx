import { Grid } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useMemo } from "react";

import { FlaggableElement } from "./FlaggableElement";

export interface Message {
  text: string;
  is_assistant: boolean;
  message_id: string;
}

export const Messages = ({ messages, post_id }: { messages: Message[]; post_id: string }) => {
  const items = messages.map((messageProps: Message, i: number) => {
    const { message_id, text } = messageProps;
    return (
      <FlaggableElement text={text} post_id={post_id} message_id={message_id} key={i + text}>
        <MessageView {...messageProps} />
      </FlaggableElement>
    );
  });
  // Maybe also show a legend of the colors?
  return <Grid gap={2}>{items}</Grid>;
};

export const MessageView = ({ is_assistant, text, message_id }: Message) => {
  const { colorMode } = useColorMode();

  const bgColor = useMemo(() => {
    if (colorMode === "light") {
      return is_assistant ? "bg-slate-800" : "bg-sky-900";
    } else {
      return is_assistant ? "bg-black" : "bg-sky-900";
    }
  }, [colorMode, is_assistant]);

  return <div className={`${bgColor} p-4 rounded-md text-white whitespace-pre-wrap`}>{text}</div>;
};
