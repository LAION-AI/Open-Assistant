import { useBreakpointValue } from "@chakra-ui/react";

export const CollapsableText = ({ text }: { text: string }) => {
  const maxLength = useBreakpointValue({ base: 220, md: 500, lg: 700, xl: 1000 });
  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    const visibleText = text.substring(0, maxLength - 3);
    return <span>{visibleText}...</span>;
  }
};
