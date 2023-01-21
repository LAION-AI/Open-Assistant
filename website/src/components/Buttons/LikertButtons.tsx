import { Button, SimpleGrid } from "@chakra-ui/react";
import { PropsWithChildren, ReactNode } from "react";

export const LikertButtons = ({
  isDisabled,
  options,
  value,
  onChange,
  "data-cy": dataCy,
}: PropsWithChildren<{
  isDisabled: boolean;
  options: ReactNode[];
  value: number;
  onChange: (value: number) => void;
  "data-cy"?: string;
}>) => {
  return (
    <SimpleGrid aria-roledescription="radiogroup" columns={options.length} spacing={[1, 4]} data-cy={dataCy}>
      {options.map((option, idx) => {
        const indexValue = idx / (options.length - 1);
        return (
          <Button
            aria-roledescription="radio"
            aria-checked={indexValue === value}
            key={idx}
            onClick={() => {
              onChange(indexValue === value ? null : indexValue);
            }}
            isDisabled={isDisabled}
            isActive={indexValue === value}
          >
            {option}
          </Button>
        );
      })}
    </SimpleGrid>
  );
};
