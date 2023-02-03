import { Flag, LucideIcon, ThumbsDown, ThumbsUp } from "lucide-react";

export const emojiIcons: { [emoji: string]: LucideIcon } = {
  "+1": ThumbsUp,
  "-1": ThumbsDown,
  flag: Flag,
  red_flag: Flag,
};

export const isKnownEmoji = (emoji: string) => !!emojiIcons[emoji];
