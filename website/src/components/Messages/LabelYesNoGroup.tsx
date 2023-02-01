import { Button, HStack, Text, Tooltip } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";

interface LabelYesNoGroupProps {
  values: number[];
  labelNames: string[];
  requiredLabels?: string[];
  isEditable?: boolean;
  onChange: (values: number[]) => void;
}

export const LabelYesNoGroup = ({
  values,
  labelNames,
  requiredLabels = [],
  isEditable = true,
  onChange,
}: LabelYesNoGroupProps) => {
  const { t } = useTranslation("labelling");
  return (
    <>
      {labelNames.map((name, idx) => {
        return (
          <YesNoQuestion
            key={name}
            question={t(getTypeSafei18nKey(`${name}.question`))}
            value={values[idx] === null ? null : values[idx] > 0.1 ? true : false}
            onChange={(value) => {
              const newValues = values.slice();
              newValues[idx] = value;
              onChange(newValues);
            }}
            isEditable={isEditable}
            isRequired={requiredLabels.includes(name)}
          />
        );
      })}
    </>
  );
};

const YesNoQuestion = ({
  isEditable,
  question,
  value,
  isRequired,
  onChange,
}: {
  isEditable: boolean;
  question: string;
  value: boolean;
  isRequired?: boolean;
  onChange: (boolean) => void;
}) => {
  const { t } = useTranslation();
  return (
    <div data-cy="label-question" style={{ maxWidth: "30em" }}>
      <Text display="inline">
        {question}
        {isRequired ? <RequiredMark /> : undefined}
      </Text>
      <HStack style={{ float: "right" }}>
        <Button
          data-cy="yes"
          isDisabled={!isEditable}
          colorScheme={value === true ? "blue" : undefined}
          onClick={() => onChange(isRequired ? true : value === null ? true : null)}
        >
          {t("yes")}
        </Button>
        <Button
          data-cy="no"
          isDisabled={!isEditable}
          colorScheme={value === false ? "blue" : undefined}
          onClick={() => onChange(isRequired ? false : value === null ? false : null)}
        >
          {t("no")}
        </Button>
      </HStack>
    </div>
  );
};

const RequiredMark = () => (
  <Tooltip label="Required">
    <span style={{ color: "red" }}>*</span>
  </Tooltip>
);
