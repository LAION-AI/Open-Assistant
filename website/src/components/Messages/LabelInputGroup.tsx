import { Text, VStack } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { Label } from "src/types/Tasks";

import { LabelLikertGroup } from "../Survey/LabelLikertGroup";
import { LabelFlagGroup } from "./LabelFlagGroup";
import { LabelYesNoGroup } from "./LabelYesNoGroup";

interface LabelInputGroupProps {
  values: number[];
  labels: Label[];
  requiredLabels?: string[];
  isEditable?: boolean;
  onChange: (values: number[]) => void;
}

export const LabelInputGroup = ({ labels, values, requiredLabels, isEditable, onChange }: LabelInputGroupProps) => {
  const { t } = useTranslation("labelling");
  const yesNoIndexes = labels.map((label, idx) => (label.widget === "yes_no" ? idx : null)).filter((v) => v !== null);
  const flagIndexes = labels.map((label, idx) => (label.widget === "flag" ? idx : null)).filter((v) => v !== null);
  const likertIndexes = labels.map((label, idx) => (label.widget === "likert" ? idx : null)).filter((v) => v !== null);

  return (
    <VStack alignItems="stretch" spacing={6}>
      {yesNoIndexes.length > 0 && (
        <VStack alignItems="stretch" spacing={2}>
          <Text>{t("label_yes_no_instruction")}</Text>
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
          <Text>{t("label_flag_instruction")}</Text>
          <LabelFlagGroup
            values={flagIndexes.map((idx) => values[idx])}
            labelNames={flagIndexes.map((idx) => labels[idx].name)}
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
          <Text>{t("label_likert_instruction")}</Text>
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
