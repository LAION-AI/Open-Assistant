import { FlaggableElement } from "./FlaggableElement";
import { useColorMode } from "@chakra-ui/react";

export interface Message {
  text: string;
  is_assistant: boolean;
}

const getBgColor = (isAssistant: boolean, colorMode: "light" | "dark") => {
  if (colorMode === "light") {
    return isAssistant ? "bg-slate-800" : "bg-sky-900";
  } else {
    return isAssistant ? "bg-black" : "bg-sky-900";
  }
};

export const Messages = ({ messages, post_id }: { messages: Message[]; post_id: string }) => {
  const { colorMode } = useColorMode();

  const items = messages.map(({ text, is_assistant }: Message, i: number) => {
    return (
      <div className="flex" key={i + text}>
        <FlaggableElement text={text} post_id={post_id}>
          <div
            key={i + text}
            className={`${getBgColor(
              is_assistant,
              colorMode
            )} p-4 my-2 rounded-xl text-white whitespace-pre-wrap float-left mr-3`}
          >
            {text}
          </div>
        </FlaggableElement>
      </div>
    );
  });
  return <>{items}</>;
};
