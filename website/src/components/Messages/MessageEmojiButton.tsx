import { Button } from "@chakra-ui/react";
import { BoxSelect, Flag, LucideProps, ThumbsDown, ThumbsUp } from "lucide-react";
import { ReactElement } from "react";
import { MessageEmoji } from "src/types/Conversation";

type EmojiIconPurpose = "MINI_BUTTON" | "NORMAL";

const defaultIconProps: (purpose: EmojiIconPurpose) => LucideProps = (purpose: EmojiIconPurpose) => {
  if (purpose === "MINI_BUTTON") return { height: "1em" };
  return {};
};

export const getEmojiIcon = (name: string, purpose: EmojiIconPurpose): ReactElement => {
  switch (name) {
    case "+1":
      return <ThumbsUp {...defaultIconProps(purpose)} />;
    case "-1":
      return <ThumbsDown {...defaultIconProps(purpose)} />;
    case "flag":
    case "red_flag":
      return <Flag {...defaultIconProps(purpose)} />;
    default:
      return <BoxSelect {...defaultIconProps(purpose)} />;
  }
};

interface MessageEmojiButtonProps {
  emoji: MessageEmoji;
  checked?: boolean;
  onClick: () => void;
}

export const MessageEmojiButton = ({ emoji, checked, onClick }: MessageEmojiButtonProps) => {
  return (
    <Button
      onClick={onClick}
      variant={checked ? "solid" : "ghost"}
      colorScheme={checked ? "blue" : undefined}
      size="sm"
      height="1.6em"
      minWidth={0}
      padding="0"
    >
      {getEmojiIcon(emoji.name, "MINI_BUTTON")}
      <span style={{ position: "relative", left: "-0.2em", marginRight: "0.25em" }}>{emoji.count}</span>
    </Button>
  );
};
