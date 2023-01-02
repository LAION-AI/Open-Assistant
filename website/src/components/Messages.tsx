import { FlaggableElement } from "./FlaggableElement";

export interface Message {
  text: string;
  is_assistant: boolean;
}

const getColor = (isAssistant: boolean) => (isAssistant ? "bg-slate-800" : "bg-sky-900");

export const Messages = ({ messages, post_id }: { messages: Message[]; post_id: string }) => {
  const items = messages.map(({ text, is_assistant }: Message, i: number) => {
    return (
      <div className="flex" key={i + text}>
        <FlaggableElement text={text} post_id={post_id}>
          <div
            key={i + text}
            className={`${getColor(is_assistant)} p-4 my-1 rounded-xl text-white whitespace-pre-wrap float-left mr-3`}
          >
            {text}
          </div>
        </FlaggableElement>
      </div>
    );
  });
  // Maybe also show a legend of the colors?
  return <>{items}</>;
};
