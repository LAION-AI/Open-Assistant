export interface Message {
  text: string;
  is_assistant: boolean;
}

const getColor = (isAssistant: boolean) => (isAssistant ? "bg-slate-800" : "bg-sky-900");

export const Messages = ({ messages }: { messages: Message[] }) => {
  const items = messages.map(({ text, is_assistant }: Message, i: number) => {
    return (
      <div key={i + text} className={`${getColor(is_assistant)} p-4 my-1 rounded-xl text-white whitespace-pre-wrap`}>
        {text}
      </div>
    );
  });
  // Maybe also show a legend of the colors?
  return <>{items}</>;
};
