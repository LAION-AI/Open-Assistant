import { Button } from "@chakra-ui/react";
import { useHasRole } from "src/hooks/auth/useHasRole";
import { MessageEmoji } from "src/types/Conversation";
import { emojiIcons } from "src/types/Emoji";

interface MessageEmojiButtonProps {
  emoji: MessageEmoji;
  checked?: boolean;
  onClick: () => void;
  userIsAuthor: boolean;
  disabled?: boolean;
  userReacted: boolean;
}

export const MessageEmojiButton = ({
  emoji,
  checked,
  onClick,
  userIsAuthor,
  disabled,
  userReacted,
}: MessageEmojiButtonProps) => {
  const EmojiIcon = emojiIcons.get(emoji.name);
  const isAdmin = useHasRole("admin");

  if (!EmojiIcon) return null;

  const isDisabled = !!(userIsAuthor ? true : disabled);
  const showCount = (emoji.count > 0 && userReacted) || userIsAuthor || isAdmin;

  return (
    <Button
      onClick={onClick}
      variant={checked ? "solid" : "ghost"}
      colorScheme={checked ? "blue" : undefined}
      size="sm"
      height="1.6em"
      minWidth={0}
      padding="0"
      disabled={disabled}
      sx={{
        ":hover": {
          backgroundColor: isDisabled ? "transparent" : undefined,
        },
      }}
      color={isDisabled ? "gray.500" : undefined}
    >
      <EmojiIcon style={{ height: "1em" }} />
      {showCount && <span style={{ marginInlineEnd: "0.25em" }}>{emoji.count}</span>}
    </Button>
  );
};
