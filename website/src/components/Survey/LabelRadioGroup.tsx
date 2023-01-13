import { Box, Button, Flex, useColorMode } from "@chakra-ui/react";
import { useId, useState } from "react";
import { colors } from "src/styles/Theme/colors";

interface LabelRadioGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
  isDisabled?: boolean;
}

export const LabelRadioGroup = (props: LabelRadioGroupProps) => {
  const [labelValues, setLabelValues] = useState<number[]>(Array.from({ length: props.labelIDs.length }).map(() => 0));
  const [interactionFlag, setInteractionFlag] = useState(false);

  return (
    <Flex direction="column" justify="center">
      {props.labelIDs.map((labelId, idx) => (
        <LabelRadioItem
          key={idx}
          labelId={labelId}
          labelValue={labelValues[idx]}
          clickHandler={(newValue) => {
            const newState = labelValues.slice();
            newState[idx] = newValue;
            props.onChange(labelValues);
            setLabelValues(newState);
            if (!interactionFlag) setInteractionFlag(true);
          }}
          states={[
            { text: "No", value: 0 },
            { text: "Yes", value: 1 },
          ]}
          isDisabled={props.isDisabled}
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
  labelId: string;
  labelValue: number;
  clickHandler: (newVal: number) => unknown;
  states: ButtonState[];
  isDisabled: boolean;
  interactionFlag: boolean;
}

const LabelRadioItem = (props: LabelRadioItemProps) => {
  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass = colorMode === "light" ? `text-${colors.light.text}` : `text-${colors.dark.text}`;

  return (
    <Box>
      <label className="text-sm" htmlFor={id}>
        {/* TODO: display real text instead of just the id */}
        <span className={labelTextClass}>{props.labelId}</span>
      </label>
      <Flex direction="row" gap={6} justify="center">
        {props.states.map((item, idx) => (
          <Button
            colorScheme={item.value === props.labelValue && props.interactionFlag ? item.colorScheme || "blue" : "gray"}
            isDisabled={props.isDisabled}
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
