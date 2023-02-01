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

interface ExplainProps {
  explanation: string[];
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
            <Text key={idx}>{paragraph}</Text>
          ))}
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
