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
import { InformationCircleIcon } from "@heroicons/react/20/solid";

interface ExplainProps {
  explanation: string[];
}

export const Explain = ({ explanation }: ExplainProps) => {
  return (
    <Popover>
      <PopoverTrigger>
        <IconButton
          aria-label="explanation"
          variant="link"
          size="xs"
          icon={<InformationCircleIcon className="h-4 w-4" />}
        ></IconButton>
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
