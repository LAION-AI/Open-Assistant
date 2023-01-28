import { Button, Flex } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";

interface LabelFlagGroupProps {
  values: number[];
  labelNames: string[];
  isEditable?: boolean;
  onChange: (values: number[]) => void;
}

export const LabelFlagGroup = ({ values, labelNames, isEditable = true, onChange }: LabelFlagGroupProps) => {
  const { t } = useTranslation("labelling");
  return (
    <Flex wrap="wrap" gap="4">
      {labelNames.map((name, idx) => (
        <Button
          key={name}
          onClick={() => {
            const newValues = values.slice();
            newValues[idx] = newValues[idx] ? 0 : 1;
            onChange(newValues);
          }}
          isDisabled={!isEditable}
          colorScheme={values[idx] === 1 ? "blue" : undefined}
          style={{ wordWrap: "break-word" }}
        >
          {t(getTypeSafei18nKey(name))}
        </Button>
      ))}
    </Flex>
  );
};
