import {
  IconButton,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Text,
} from "@chakra-ui/react";
import { Info } from "lucide-react";
import { ReactElement } from "react";

interface ExplainProps {
  explanation: ReactElement[] | string[];
}

export const Explain = ({ explanation }: ExplainProps) => {
  return (
    <Popover>
      <PopoverTrigger>
        <IconButton aria-label="explanation" variant="link" size="xs" icon={<Info size="16" />}></IconButton>
      </PopoverTrigger>
      <PopoverContent>
        <PopoverArrow />
        <PopoverCloseButton />
        <PopoverBody>
          {explanation.map((paragraph, idx) => (
            <Text key={idx} mt={idx === 0 ? 0 : 3}>
              {paragraph}
            </Text>
          ))}
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
