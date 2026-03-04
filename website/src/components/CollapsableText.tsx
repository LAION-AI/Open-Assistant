import { useBreakpointValue } from "@chakra-ui/react";

interface CollapsableTextProps {
  text: string;
  isCollapsed?: boolean;
}

export const CollapsableText = ({ text, isCollapsed = true }: CollapsableTextProps) => {
  const maxLength = useBreakpointValue({ base: 220, md: 500, lg: 700, xl: 1000 });
  
  // If not collapsed or text is short, show full text
  if (!isCollapsed || typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  }
  
  // Show collapsed text
  const visibleText = text.substring(0, maxLength - 3);
  return <span>{visibleText}...</span>;
};
