import {
  Button,
  Checkbox,
  Flex,
  Grid,
  Popover,
  PopoverAnchor,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Spacer,
  Tooltip,
  useBoolean,
  useColorMode,
  useColorModeValue,
  useId,
} from "@chakra-ui/react";
import { FlagIcon, QuestionMarkCircleIcon } from "@heroicons/react/20/solid";
import { useState } from "react";
import poster from "src/lib/poster";
import { colors } from "styles/Theme/colors";
import useSWRMutation from "swr/mutation";

interface textFlagLabels {
  attributeName: string;
  labelText: string;
  additionalExplanation?: string;
}

export const FlaggableElement = (props) => {
  const [isEditing, setIsEditing] = useBoolean();
  const flaggable_labels = props.flaggable_labels;
  const TEXT_LABEL_FLAGS = flaggable_labels.valid_labels.map((valid_label) => {
    return {
      attributeName: valid_label.name,
      labelText: valid_label.display_text,
      additionalExplanation: valid_label.help_text,
    };
  });
  const { trigger } = useSWRMutation("/api/set_label", poster, {
    onSuccess: () => {
      setIsEditing.off;
    },
  });

  const submitResponse = () => {
    const label_map: Map<string, number> = new Map();
    TEXT_LABEL_FLAGS.forEach((flag, i) => {
      if (checkboxValues[i]) {
        label_map.set(flag.attributeName, sliderValues[i]);
      }
    });
    trigger({
      message_id: props.message_id,
      post_id: props.post_id,
      label_map: Object.fromEntries(label_map),
      text: props.text,
    });
  };
  const [checkboxValues, setCheckboxValues] = useState(new Array(TEXT_LABEL_FLAGS.length).fill(false));
  const [sliderValues, setSliderValues] = useState(new Array(TEXT_LABEL_FLAGS.length).fill(1));

  const handleCheckboxState = (isChecked, idx) => {
    setCheckboxValues(
      checkboxValues.map((val, i) => {
        return i == idx ? isChecked : val;
      })
    );
  };
  const handleSliderState = (newVal, idx) => {
    setSliderValues(
      sliderValues.map((val, i) => {
        return i == idx ? newVal : val;
      })
    );
  };

  return (
    <Popover
      isOpen={isEditing}
      onOpen={setIsEditing.on}
      onClose={setIsEditing.off}
      closeOnBlur={false}
      isLazy
      lazyBehavior="keepMounted"
    >
      <Grid templateColumns="1fr min-content" gap={2}>
        <PopoverAnchor>{props.children}</PopoverAnchor>
        <Tooltip hasArrow label="Report" bg="red.600">
          <div>
            <PopoverTrigger>
              <Button h="full">
                <FlagIcon className="w-4 text-gray-400 group-hover:text-gray-500" aria-hidden="true" />
              </Button>
            </PopoverTrigger>
          </div>
        </Tooltip>
      </Grid>

      <PopoverContent width="fit-content">
        <PopoverArrow />
        <div className="relative h-4">
          <PopoverCloseButton />
        </div>
        <PopoverBody>
          {TEXT_LABEL_FLAGS.map((option, i) => (
            <FlagCheckbox
              option={option}
              key={i}
              idx={i}
              checkboxValues={checkboxValues}
              sliderValues={sliderValues}
              checkboxHandler={handleCheckboxState}
              sliderHandler={handleSliderState}
            />
          ))}
          <Flex justify="center">
            <Button
              isDisabled={!checkboxValues.some(Boolean)}
              onClick={submitResponse}
              className={`bg-indigo-600 text-${useColorModeValue(
                colors.light.text,
                colors.dark.text
              )} hover:bg-indigo-700`}
            >
              Report
            </Button>
          </Flex>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export function FlagCheckbox(props: {
  option: textFlagLabels;
  idx: number;
  checkboxValues: boolean[];
  sliderValues: number[];
  checkboxHandler: (newVal: boolean, idx: number) => void;
  sliderHandler: (newVal: number, idx: number) => void;
}): JSX.Element {
  let AdditionalExplanation = null;
  if (props.option.additionalExplanation) {
    AdditionalExplanation = (
      <a href="#" className="group flex items-center space-x-2.5 text-sm ">
        <QuestionMarkCircleIcon
          className="flex h-5 w-5 ml-3 text-gray-400 group-hover:text-gray-500"
          aria-hidden="true"
        />
      </a>
    );
  }

  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass =
    colorMode === "light"
      ? `text-${colors.light.text} hover:text-blue-700 float-left`
      : `text-${colors.dark.text} hover:text-blue-400 float-left`;

  return (
    <Flex gap={1}>
      <Checkbox
        id={id}
        onChange={(e) => {
          props.checkboxHandler(e.target.checked, props.idx);
        }}
      />
      <label className="text-sm form-check-label" htmlFor={id}>
        <span className={labelTextClass}>{props.option.labelText}</span>
        {AdditionalExplanation}
      </label>
      <Spacer />
      <Slider
        width="100px"
        isDisabled={!props.checkboxValues[props.idx]}
        defaultValue={100}
        onChangeEnd={(val) => {
          props.sliderHandler(val / 100, props.idx);
        }}
      >
        <SliderTrack>
          <SliderFilledTrack />
          <SliderThumb />
        </SliderTrack>
      </Slider>
    </Flex>
  );
}
