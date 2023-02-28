import { Button, ButtonProps } from "@chakra-ui/react";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { MessageEmoji } from "src/types/Conversation";
import { emojiIcons } from "src/types/Emoji";

interface MessageEmojiButtonProps {
  emoji: MessageEmoji;
  checked?: boolean;
  onClick?: () => void;
  userIsAuthor: boolean;
  disabled?: boolean;
  userReacted: boolean;
  sx?: ButtonProps["sx"];
}

export const MessageEmojiButton = ({
  emoji,
  checked,
  onClick,
  userIsAuthor,
  disabled,
  userReacted,
  sx,
}: MessageEmojiButtonProps) => {
  const EmojiIcon = emojiIcons.get(emoji.name);
  const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);

  if (!EmojiIcon) return null;

  const isDisabled = !!(userIsAuthor ? true : disabled);
  const showCount = (emoji.count > 0 && userReacted) || userIsAuthor || isAdminOrMod;

  return (
    <Button
      onClick={onClick}
      variant={checked ? "solid" : "ghost"}
      colorScheme={checked ? "blue" : undefined}
      size="sm"
      height="1.6em"
      minWidth={0}
      padding="0"
      isDisabled={disabled}
      sx={{
        ":hover": {
          backgroundColor: isDisabled ? "transparent" : undefined,
        },
        ...sx,
      }}
      color={isDisabled ? (checked ? "gray.700" : "gray.500") : undefined}
    >
      <EmojiIcon style={{ height: "1em" }} />
      {showCount && <span style={{ marginInlineEnd: "0.25em" }}>{emoji.count}</span>}
    </Button>
  );
};
