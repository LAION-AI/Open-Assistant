import { Radio, RadioGroup } from "@chakra-ui/react";
import { PropsWithChildren } from "react";

export const LikertButtons = ({
  isDisabled,
  count,
  onChange,
  "data-cy": dataCy,
}: PropsWithChildren<{
  isDisabled: boolean;
  count: number;
  onChange: (value: number) => void;
  "data-cy"?: string;
}>) => {
  const valueMap = Object.fromEntries(Array.from({ length: count }, (_, idx) => [`${idx}`, idx / (count - 1)]));

  return (
    <RadioGroup
      data-cy={dataCy}
      isDisabled={isDisabled}
      onChange={(value) => {
        onChange(valueMap[value]);
      }}
      style={{ display: "flex", justifyContent: "space-between" }}
    >
      {Object.keys(valueMap).map((value) => {
        return (
          <Radio key={value} value={value} borderColor="gray.400" data-cy="radio-option" size="md" padding="0.6em" />
        );
      })}
    </RadioGroup>
  );
};
