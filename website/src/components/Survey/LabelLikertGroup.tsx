import { Box, Grid, GridItem, Text, useColorModeValue } from "@chakra-ui/react";
import React from "react";
import { useState } from "react";
import { LikertButtons } from "src/components/Buttons/LikertButtons";
import { Explain } from "src/components/Explain";

interface LabelInputGroupProps {
  labelIDs: Array<string>;
  onChange: (values: number[]) => unknown;
  isEditable?: boolean;
}

interface LabelInfo {
  zeroText: string;
  oneText: string;
  zeroDescription: string[];
  oneDescription: string[];
  inverted: boolean;
}

const getLabelInfo = (label: string): LabelInfo => {
  switch (label) {
    case "spam":
      return {
        zeroText: "Not Spam",
        zeroDescription: ["Suitable for training Open Assistant."],
        oneText: "Spam",
        oneDescription: [
          "Seems to be intentionally low-quality or irrelevant",
          'We consider the following unwanted content as spam: trolling, intentional undermining of our purpose, illegal material, material that violates our code of conduct, and other things that are inappropriate for our dataset. We collect these under the common heading of "spam".',
          "This is not an assessment of whether this message is the best possible answer. Especially for prompts or user-replies, we very much want to retain all kinds of responses in the dataset, so that the assistant can learn to reply appropriately.",
          "Please mark this text as spam only if it is clearly unsuited to be part of our dataset, as outlined above, and try not to make any subjective value-judgments beyond that.",
        ],
        inverted: true,
      };
    case "fails_task":
      return {
        zeroText: "Follows Instructions",
        zeroDescription: [],
        oneText: "Fails Task",
        oneDescription: ["Fails to follow the correct instruction / task"],
        inverted: true,
      };
    case "not_appropriate":
      return {
        zeroText: "Appropriate",
        zeroDescription: [],
        oneText: "Inappropriate",
        oneDescription: ["Inappropriate for customer assistant"],
        inverted: true,
      };
    case "violence":
      return {
        zeroText: "Harmless",
        zeroDescription: [],
        oneText: "Violent",
        oneDescription: ["Encourages or fails to discourage violence/abuse/terrorism/self-harm"],
        inverted: true,
      };
    case "excessive_harm":
      return {
        zeroText: "Safe",
        zeroDescription: [],
        oneText: "Harmful",
        oneDescription: [
          "Content likely to cause excessive harm not justifiable in the context",
          "Harm refers to physical or mental damage or injury to someone or something. Excessive refers to a reasonable threshold of harm in the context, for instance damaging skin is not excessive in the context of surgery.",
        ],
        inverted: true,
      };
    case "sexual_content":
      return {
        zeroText: "Non Sexual",
        zeroDescription: [],
        oneText: "Sexual",
        oneDescription: ["Contains sexual content"],
        inverted: true,
      };
    case "toxicity":
      return {
        zeroText: "Polite",
        zeroDescription: [],
        oneText: "Rude",
        oneDescription: ["Contains rude, abusive, profane or insulting content"],
        inverted: true,
      };
    case "moral_judgement":
      return {
        zeroText: "Non-Judgemental",
        zeroDescription: [],
        oneText: "Judgemental",
        oneDescription: ["Expresses moral judgement"],
        inverted: true,
      };
    case "political_content":
      return {
        zeroText: "Apolitical",
        zeroDescription: [],
        oneText: "Political",
        oneDescription: ["Expresses political views"],
        inverted: true,
      };
    case "humor":
      return {
        zeroText: "Serious",
        zeroDescription: [],
        oneText: "Humorous",
        oneDescription: ["Contains humorous content including sarcasm"],
        inverted: false,
      };
    case "hate_speech":
      return {
        zeroText: "Safe",
        zeroDescription: [],
        oneText: "Hateful",
        oneDescription: [
          "Content is abusive or threatening and expresses prejudice against a protected characteristic",
          "Prejudice refers to preconceived views not based on reason. Protected characteristics include gender, ethnicity, religion, sexual orientation, and similar characteristics.",
        ],
        inverted: true,
      };
    case "threat":
      return {
        zeroText: "Safe",
        zeroDescription: [],
        oneText: "Threatening",
        oneDescription: ["Contains a threat against a person or persons"],
        inverted: true,
      };
    case "misleading":
      return {
        zeroText: "Accurate",
        zeroDescription: [],
        oneText: "Misleading",
        oneDescription: ["Contains text which is incorrect or misleading"],
        inverted: true,
      };
    case "helpfulness":
      return {
        zeroText: "Unhelpful",
        zeroDescription: [],
        oneText: "Helpful",
        oneDescription: ["Completes the task to a high standard"],
        inverted: false,
      };
    case "creative":
      return {
        zeroText: "Boring",
        zeroDescription: [],
        oneText: "Creative",
        oneDescription: ["Expresses creativity in responding to the task"],
        inverted: false,
      };
    case "pii":
      return {
        zeroText: "Clean",
        zeroDescription: [],
        oneText: "Contains PII",
        oneDescription: ["Contains personally identifying information"],
        inverted: false,
      };
    case "quality":
      return {
        zeroText: "Low Quality",
        zeroDescription: [],
        oneText: "High Quality",
        oneDescription: [],
        inverted: false,
      };
    case "creativity":
      return {
        zeroText: "Ordinary",
        zeroDescription: [],
        oneText: "Creative",
        oneDescription: [],
        inverted: false,
      };
    default:
      return {
        zeroText: `!${label}`,
        zeroDescription: [],
        oneText: label,
        oneDescription: [],
        inverted: false,
      };
  }
};

export const LabelLikertGroup = ({ labelIDs, onChange, isEditable = true }: LabelInputGroupProps) => {
  const [labelValues, setLabelValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => null));

  const cardColor = useColorModeValue("gray.50", "gray.800");

  return (
    <Grid templateColumns={"minmax(min-content, 30em)"} rowGap={2}>
      {labelIDs.map((labelId, idx) => {
        const { zeroText, oneText, zeroDescription, oneDescription, inverted } = getLabelInfo(labelId);

        let textA = zeroText;
        let textB = oneText;
        let descriptionA = zeroDescription;
        let descriptionB = oneDescription;
        if (inverted) [textA, textB, descriptionA, descriptionB] = [textB, textA, descriptionB, descriptionA];

        return (
          <Box key={idx} padding={2} bg={cardColor} borderRadius="md" position="relative">
            <Grid
              templateColumns={{
                base: "minmax(0, 1fr) minmax(0, 1fr)",
                sm: "minmax(0, 1fr) auto minmax(0, 1fr)",
              }}
              alignItems="center"
            >
              <Text as="div" display="flex" alignItems="center">
                {textA}
                {descriptionA.length > 0 ? <Explain explanation={descriptionA} /> : null}
              </Text>
              <GridItem colSpan={{ base: 2, sm: 1 }} gridColumnStart={{ base: 1, sm: 2 }} gridRow={{ base: 2, sm: 1 }}>
                <LikertButtons
                  isDisabled={!isEditable}
                  count={5}
                  data-cy="label-options"
                  onChange={(value) => {
                    const newState = labelValues.slice();
                    newState[idx] = value === null ? null : inverted ? 1 - value : value;
                    onChange(newState);
                    setLabelValues(newState);
                  }}
                />
              </GridItem>
              <GridItem>
                <Text as="div" display="flex" alignItems="center" justifyContent="end">
                  {textB}
                  {descriptionB.length > 0 ? <Explain explanation={descriptionB} /> : null}
                </Text>
              </GridItem>
            </Grid>
          </Box>
        );
      })}
    </Grid>
  );
};
