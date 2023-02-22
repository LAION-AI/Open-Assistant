import { Button, Flex, Tooltip } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { getLocaleDisplayName } from "src/lib/languages";

interface LabelFlagGroupProps {
  values: number[];
  labelNames: string[];
  expectedLanguage: string;
  isEditable?: boolean;
  onChange: (values: number[]) => void;
}

export const LabelFlagGroup = ({
  values,
  labelNames,
  expectedLanguage,
  isEditable = true,
  onChange,
}: LabelFlagGroupProps) => {
  const { t } = useTranslation("labelling");
  const currentLanguage = useCurrentLocale();
  const expectedLanguageName = getLocaleDisplayName(expectedLanguage, currentLanguage);
  return (
    <Flex wrap="wrap" gap="4">
      {labelNames.map((name, idx) => (
        <Tooltip
          key={name}
          label={`${t(getTypeSafei18nKey(`${name}.explanation`), `${name}.explanation`, {
            language: expectedLanguageName,
          })}`}
        >
          <Button
            onClick={() => {
              const newValues = values.slice();
              newValues[idx] = newValues[idx] ? 0 : 1;
              onChange(newValues);
            }}
            isDisabled={!isEditable}
            colorScheme={values[idx] === 1 ? "blue" : undefined}
          >
            {t(getTypeSafei18nKey(`${name}`), name, { language: expectedLanguageName })}
          </Button>
        </Tooltip>
      ))}
    </Flex>
  );
};
