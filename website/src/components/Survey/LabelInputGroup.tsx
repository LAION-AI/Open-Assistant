import { Box, Flex, Grid, Spacer, Text, useColorModeValue, VStack } from "@chakra-ui/react";
import React from "react";
import { useState } from "react";
import { TbChevronLeft, TbChevronRight, TbChevronsLeft, TbChevronsRight } from "react-icons/tb";
import { LikertButtons } from "src/components/Buttons/LikertButtons";
import { Explain } from "src/components/Explain";

interface LabelInputGroupProps {
  labelIDs: Array<string>;
  simple?: boolean;
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

// This should be moved to the valid labels api endpoint
const label_messages: {
  [label: string]: LabelInfo;
} = {
  spam: {
    zeroText: "Suitable for Training",
    zeroDescription: ["Suitable for training Open Assistant."],
    oneText: "Spam",
    oneDescription: [
      "Seems to be intentionally low-quality or irrelevant",
      'We consider the following unwanted content as spam: trolling, intentional undermining of our purpose, illegal material, material that violates our code of conduct, and other things that are inappropriate for our dataset. We collect these under the common heading of "spam".',
      "This is not an assessment of whether this message is the best possible answer. Especially for prompts or user-replies, we very much want to retain all kinds of responses in the dataset, so that the assistant can learn to reply appropriately.",
      "Please mark this text as spam only if it is clearly unsuited to be part of our dataset, as outlined above, and try not to make any subjective value-judgments beyond that.",
    ],
    inverted: true,
  },
  fails_task: {
    zeroText: "Follows Instructions",
    zeroDescription: [],
    oneText: "Fails Task",
    oneDescription: ["Fails to follow the correct instruction / task"],
    inverted: true,
  },
  not_appropriate: {
    zeroText: "Appropriate",
    zeroDescription: [],
    oneText: "Inappropriate",
    oneDescription: ["Inappropriate for customer assistant"],
    inverted: true,
  },
  violence: {
    zeroText: "Harmless",
    zeroDescription: [],
    oneText: "Encourages Violence",
    oneDescription: ["Encourages or fails to discourage violence/abuse/terrorism/self-harm"],
    inverted: true,
  },
  excessive_harm: {
    zeroText: "Safe",
    zeroDescription: [],
    oneText: "Causes Harm",
    oneDescription: [
      "Content likely to cause excessive harm not justifiable in the context",
      "Harm refers to physical or mental damage or injury to someone or something. Excessive refers to a reasonable threshold of harm in the context, for instance damaging skin is not excessive in the context of surgery.",
    ],
    inverted: true,
  },
  sexual_content: {
    zeroText: "Non Sexual",
    zeroDescription: [],
    oneText: "Sexual Content",
    oneDescription: ["Contains sexual content"],
    inverted: true,
  },
  toxicity: {
    zeroText: "Non Toxic",
    zeroDescription: [],
    oneText: "Rude / Toxic",
    oneDescription: ["Contains rude, abusive, profane or insulting content"],
    inverted: true,
  },
  moral_judgement: {
    zeroText: "Non-Judgemental",
    zeroDescription: [],
    oneText: "Judgemental",
    oneDescription: ["Expresses moral judgement"],
    inverted: true,
  },
  political_content: {
    zeroText: "Apolitical",
    zeroDescription: [],
    oneText: "Political",
    oneDescription: ["Expresses political views"],
    inverted: true,
  },
  humor: {
    zeroText: "Serious",
    zeroDescription: [],
    oneText: "Humorous / Sarcastic",
    oneDescription: ["Contains humorous content including sarcasm"],
    inverted: false,
  },
  hate_speech: {
    zeroText: "Safe",
    zeroDescription: [],
    oneText: "Hateful",
    oneDescription: [
      "Content is abusive or threatening and expresses prejudice against a protected characteristic",
      "Prejudice refers to preconceived views not based on reason. Protected characteristics include gender, ethnicity, religion, sexual orientation, and similar characteristics.",
    ],
    inverted: true,
  },
  threat: {
    zeroText: "Safe",
    zeroDescription: [],
    oneText: "Contains Threat",
    oneDescription: ["Contains a threat against a person or persons"],
    inverted: true,
  },
  misleading: {
    zeroText: "Accurate",
    zeroDescription: [],
    oneText: "Misleading",
    oneDescription: ["Contains text which is incorrect or misleading"],
    inverted: true,
  },
  helpful: {
    zeroText: "Unhelful",
    zeroDescription: [],
    oneText: "Helpful",
    oneDescription: ["Completes the task to a high standard"],
    inverted: false,
  },
  creative: {
    zeroText: "Boring",
    zeroDescription: [],
    oneText: "Creative",
    oneDescription: ["Expresses creativity in responding to the task"],
    inverted: false,
  },
};

export const LabelInputGroup = ({ labelIDs, onChange, isEditable = true }: LabelInputGroupProps) => {
  const [labelValues, setLabelValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => null));

  const cardColor = useColorModeValue("gray.50", "gray.800");

  return (
    <Grid templateColumns={"minmax(min-content, 30em)"} rowGap={2}>
      {labelIDs.map((labelId, idx) => {
        const { zeroText, oneText, zeroDescription, oneDescription, inverted } = label_messages[labelId];

        let textA = zeroText;
        let textB = oneText;
        let descriptionA = zeroDescription;
        let descriptionB = oneDescription;
        if (inverted) [textA, textB, descriptionA, descriptionB] = [textB, textA, descriptionB, descriptionA];

        return (
          <Box key={idx} padding={2} bg={cardColor} borderRadius="md">
            <VStack alignItems="stretch" spacing={1}>
              <Flex>
                <Text>{textA}</Text>
                {descriptionA.length > 0 ? <Explain explanation={descriptionA} /> : null}
                <Spacer minWidth="1em" />
                <Text textAlign="right">{textB}</Text>
                {descriptionB.length > 0 ? <Explain explanation={descriptionB} /> : null}
              </Flex>
              <LikertButtons
                isDisabled={!isEditable}
                options={[
                  <TbChevronsLeft key="<<" />,
                  <TbChevronLeft key="<" />,
                  "",
                  <TbChevronRight key=">" />,
                  <TbChevronsRight key=">>" />,
                ]}
                data-cy="label-options"
                value={labelValues[idx] === null ? null : inverted ? 1 - labelValues[idx] : labelValues[idx]}
                onChange={(value) => {
                  const newState = labelValues.slice();
                  newState[idx] = value === null ? null : inverted ? 1 - value : value;
                  onChange(newState);
                  setLabelValues(newState);
                }}
              />
            </VStack>
          </Box>
        );
      })}
    </Grid>
  );
};
