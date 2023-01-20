import {
  Box,
  Button,
  Flex,
  IconButton,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Text,
  useColorMode,
} from "@chakra-ui/react";
import { InformationCircleIcon } from "@heroicons/react/20/solid";
import { useId, useState } from "react";
import { colors } from "src/styles/Theme/colors";

interface LabelRadioGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
  isEditable?: boolean;
}

const label_messages: { [label: string]: { description: string; explanation: string[] } } = {
  spam: {
    description: "Is the message spam?",
    explanation: [
      'We consider the following unwanted content as spam: trolling, intentional undermining of our purpose, illegal material, material that violates our code of conduct, and other things that are inappropriate for our dataset. We collect these under the common heading of "spam".',
      "This is not an assessment of whether this message is the best possible answer. Especially for prompts or user-replies, we very much want to retain all kinds of responses in the dataset, so that the assistant can learn to reply appropriately.",
      "Please mark this text as spam only if it is clearly unsuited to be part of our dataset, as outlined above, and try not to make any subjective value-judgments beyond that.",
    ],
  },
};

export const LabelRadioGroup = (props: LabelRadioGroupProps) => {
  const [labelValues, setLabelValues] = useState<number[]>(Array.from({ length: props.labelIDs.length }).map(() => 0));
  const [interactionFlag, setInteractionFlag] = useState(false);

  return (
    <Flex direction="column" justify="center">
      {props.labelIDs.map((labelId, idx) => (
        <LabelRadioItem
          key={idx}
          labelText={label_messages[labelId] || { description: labelId }}
          labelValue={labelValues[idx]}
          clickHandler={(newValue) => {
            const newState = labelValues.slice();
            newState[idx] = newValue;
            props.onChange(newState);
            setLabelValues(newState);
            if (!interactionFlag) setInteractionFlag(true);
          }}
          states={[
            { text: "No", value: 0 },
            { text: "Yes", value: 1 },
          ]}
          isEditable={props.isEditable}
          interactionFlag={interactionFlag}
        />
      ))}
    </Flex>
  );
};

interface ButtonState {
  text: string;
  value: number;
  colorScheme?: string;
}

interface LabelRadioItemProps {
  labelText: { description: string; explanation?: string[] };
  labelValue: number;
  clickHandler: (newVal: number) => unknown;
  states: ButtonState[];
  isEditable: boolean;
  interactionFlag: boolean;
}

const LabelRadioItem = (props: LabelRadioItemProps) => {
  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass = colorMode === "light" ? `text-${colors.light.text}` : `text-${colors.dark.text}`;

  return (
    <Box data-cy="label-group-item" data-label-type="radio">
      <label className="text-sm" htmlFor={id}>
        {/* TODO: display real text instead of just the id */}
        <span className={labelTextClass}>{props.labelText.description}</span>
        {props.labelText.explanation ? (
          <Popover>
            <PopoverTrigger>
              <IconButton
                aria-label="explanation"
                variant="link"
                icon={<InformationCircleIcon className="h-5 w-5" />}
              ></IconButton>
            </PopoverTrigger>
            <PopoverContent>
              <PopoverArrow />
              <PopoverCloseButton />
              <PopoverBody>
                {props.labelText.explanation.map((paragraph, idx) => (
                  <Text key={idx}>{paragraph}</Text>
                ))}
              </PopoverBody>
            </PopoverContent>
          </Popover>
        ) : null}
      </label>
      <Flex direction="row" gap={6} justify="center">
        {props.states.map((item, idx) => (
          <Button
            aria-roledescription="radio-button"
            colorScheme={item.value === props.labelValue && props.interactionFlag ? item.colorScheme || "blue" : "gray"}
            isDisabled={!props.isEditable}
            size="lg"
            key={idx}
            onClick={() => props.clickHandler(item.value)}
          >
            {item.text}
          </Button>
        ))}
      </Flex>
    </Box>
  );
};
