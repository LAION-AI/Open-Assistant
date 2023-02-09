import React, { ReactNode } from "react";

export const CollapsableText = ({
  text,
  maxLength = 220,
}: {
  text: ReactNode;
  maxLength?: number;
  isDisabled?: boolean;
}) => {
  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    return <span>{text.substring(0, maxLength - 3)}...</span>;
  }
};
