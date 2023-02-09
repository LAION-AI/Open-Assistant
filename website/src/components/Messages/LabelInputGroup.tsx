import { Box, Text, VStack } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { Explain } from "src/components/Explain";
import { LabelFlagGroup } from "src/components/Messages/LabelFlagGroup";
import { LabelYesNoGroup } from "src/components/Messages/LabelYesNoGroup";
import { LabelLikertGroup } from "src/components/Survey/LabelLikertGroup";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { Label } from "src/types/Tasks";

export interface LabelInputInstructions {
  yesNoInstruction: string;
  flagInstruction: string;
  likertInstruction: string;
}

interface LabelInputGroupProps {
  values: number[];
  labels: Label[];
  requiredLabels?: string[];
  isEditable?: boolean;
  instructions: LabelInputInstructions;
  expectedLanguage: string;
  onChange: (values: number[]) => void;
}

export const LabelInputGroup = ({
  labels,
  values,
  requiredLabels,
  isEditable,
  instructions,
  expectedLanguage,
  onChange,
}: LabelInputGroupProps) => {
  const { t } = useTranslation("labelling");
  const yesNoIndexes = labels.map((label, idx) => (label.widget === "yes_no" ? idx : null)).filter((v) => v !== null);
  const flagIndexes = labels.map((label, idx) => (label.widget === "flag" ? idx : null)).filter((v) => v !== null);
  const likertIndexes = labels.map((label, idx) => (label.widget === "likert" ? idx : null)).filter((v) => v !== null);

  return (
    <VStack alignItems="stretch" spacing={6}>
      {yesNoIndexes.length > 0 && (
        <VStack alignItems="stretch" spacing={2}>
          <Text>{instructions.yesNoInstruction}</Text>
          <LabelYesNoGroup
            values={yesNoIndexes.map((idx) => values[idx])}
            labelNames={yesNoIndexes.map((idx) => labels[idx].name)}
            isEditable={isEditable}
            requiredLabels={requiredLabels}
            onChange={(yesNoValues) => {
              const newValues = values.slice();
              yesNoIndexes.forEach((idx, yesNoIndex) => (newValues[idx] = yesNoValues[yesNoIndex]));
              onChange(newValues);
            }}
          />
        </VStack>
      )}
      {flagIndexes.length > 0 && (
        <VStack alignItems="stretch" spacing={2}>
          <Box>
            <Text display="inline-block" paddingEnd={1}>
              {instructions.flagInstruction}
            </Text>
            <Explain
              explanation={flagIndexes.map(
                (idx) =>
                  `${t(getTypeSafei18nKey(labels[idx].name))}: ${t(
                    getTypeSafei18nKey(`${labels[idx].name}.explanation`)
                  )}`
              )}
            />
          </Box>
          <LabelFlagGroup
            values={flagIndexes.map((idx) => values[idx])}
            labelNames={flagIndexes.map((idx) => labels[idx].name)}
            expectedLanguage={expectedLanguage}
            isEditable={isEditable}
            onChange={(flagValues) => {
              const newValues = values.slice();
              flagIndexes.forEach((idx, flagIndex) => (newValues[idx] = flagValues[flagIndex]));
              onChange(newValues);
            }}
          />
        </VStack>
      )}
      {likertIndexes.length > 0 && (
        <VStack alignItems="stretch" spacing={2}>
          <Text>{instructions.likertInstruction}</Text>
          <LabelLikertGroup
            labelIDs={likertIndexes.map((idx) => labels[idx].name)}
            isEditable={isEditable}
            onChange={(likertValues) => {
              const newValues = values.slice();
              likertIndexes.forEach((idx, likertIndex) => (newValues[idx] = likertValues[likertIndex]));
              onChange(newValues);
            }}
          />
        </VStack>
      )}
    </VStack>
  );
};
