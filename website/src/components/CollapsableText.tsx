import { ReactNode } from "react";

export const CollapsableText = ({ text, maxLength = 220 }: { text: ReactNode; maxLength?: number }) => {
  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    const visibleText = text.substring(0, maxLength - 3);
    return <span>{visibleText}...</span>;
  }
};
