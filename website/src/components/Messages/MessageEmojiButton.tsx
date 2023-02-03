import { Button } from "@chakra-ui/react";
import { MessageEmoji } from "src/types/Conversation";
import { emojiIcons } from "src/types/Emoji";

interface MessageEmojiButtonProps {
  emoji: MessageEmoji;
  checked?: boolean;
  onClick: () => void;
}

export const MessageEmojiButton = ({ emoji, checked, onClick }: MessageEmojiButtonProps) => {
  const EmojiIcon = emojiIcons.get(emoji.name);
  if (!EmojiIcon) return <></>;
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
      <EmojiIcon style={{ height: "1em" }} />
      <span style={{ marginInlineEnd: "0.25em" }}>{emoji.count}</span>
    </Button>
  );
};
