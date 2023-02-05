import { Flag, LucideIcon, ThumbsDown, ThumbsUp } from "lucide-react";

// Note: we use a Map here rather than just an object because the optimised
// build "optimises" +1 to just 1 in the emoji name.
export const emojiIcons = new Map<string, LucideIcon>([
  ["+1", ThumbsUp],
  ["-1", ThumbsDown],
  ["flag", Flag],
  ["red_flag", Flag],
]);

export const isKnownEmoji = (emoji: string) => emojiIcons.has(emoji);
