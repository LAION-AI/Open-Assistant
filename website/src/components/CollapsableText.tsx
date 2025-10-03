import { useBreakpointValue } from "@chakra-ui/react";

interface CollapsableTextProps {
  text: string;
  disableCollapse?: boolean;
}

export const CollapsableText = ({ text, disableCollapse = false }: CollapsableTextProps) => {
  const maxLength = useBreakpointValue({ base: 220, md: 500, lg: 700, xl: 1000 });

  if (disableCollapse || typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    const visibleText = text.substring(0, maxLength - 3);
    return <span>{visibleText}...</span>;
  }
};
