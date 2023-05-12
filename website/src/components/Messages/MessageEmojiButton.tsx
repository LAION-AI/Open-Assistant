import { Button, ButtonProps, Tooltip, useColorModeValue } from "@chakra-ui/react";
import { ElementType, PropsWithChildren } from "react";
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
  forceHideCount?: boolean;
}

export const MessageEmojiButton = ({
  emoji,
  checked,
  onClick,
  userIsAuthor,
  disabled,
  userReacted,
  sx,
  forceHideCount,
}: MessageEmojiButtonProps) => {
  const EmojiIcon = emojiIcons.get(emoji.name);
  const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);

  if (!EmojiIcon) return null;

  const isDisabled = !!(userIsAuthor ? true : disabled);
  const showCount =
    forceHideCount !== undefined ? !forceHideCount : (emoji.count > 0 && userReacted) || userIsAuthor || isAdminOrMod;

  return (
    <BaseMessageEmojiButton onClick={onClick} isDisabled={isDisabled} emoji={EmojiIcon} checked={checked} sx={sx}>
      {showCount && <span style={{ marginInlineEnd: "0.25em" }}>{emoji.count}</span>}
    </BaseMessageEmojiButton>
  );
};

type BaseMessageEmojiButtonProps = PropsWithChildren<{
  emoji: ElementType<any>;
  checked?: boolean;
  onClick?: () => void;
  isDisabled?: boolean;
  sx?: ButtonProps["sx"];
  label?: string;
}>;

export const BaseMessageEmojiButton = ({
  emoji: Emoji,
  checked,
  onClick,
  isDisabled,
  sx,
  children,
  label,
}: BaseMessageEmojiButtonProps) => {
  const disabledColor = useColorModeValue("gray.500", "gray.400");
  const button = (
    <Button
      onClick={onClick}
      variant={checked ? "solid" : "ghost"}
      colorScheme={checked ? "blue" : undefined}
      size="sm"
      height="1.6em"
      minWidth={0}
      padding="0"
      isDisabled={isDisabled}
      sx={{
        ":hover": {
          backgroundColor: isDisabled ? "transparent" : undefined,
        },
        ...sx,
      }}
      color={isDisabled ? (checked ? "gray.700" : disabledColor) : undefined}
    >
      <Emoji style={{ height: "1em" }} />
      {children}
    </Button>
  );

  if (!label) {
    return button;
  }

  return (
    <Tooltip label={label} placement="top">
      {button}
    </Tooltip>
  );
};
