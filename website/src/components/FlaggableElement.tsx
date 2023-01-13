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
import { useEffect, useReducer } from "react";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import { Message } from "src/types/Conversation";
import { colors } from "styles/Theme/colors";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

interface Label {
  name: string;
  display_text: string;
  help_text: string;
}

interface LoadLabelsAction {
  type: "load_labels";
  labels: Label[];
}

interface UpdateValueAction {
  type: "update_value";
  label_index: number;
  value: number;
}

interface ToggleLabelAction {
  type: "toggle_label";
  label_index: number;
  check: boolean;
}

interface LabelValue {
  label: Label;
  checked: boolean;
  value: number;
}

interface FlagReportState {
  label_values: LabelValue[];
  submittable: boolean;
}

interface FlaggableElementProps {
  children: React.ReactNode;
  message: Message;
}

export const FlaggableElement = (props: FlaggableElementProps) => {
  const [report, updateReport] = useReducer(
    (state: FlagReportState, action: LoadLabelsAction | UpdateValueAction | ToggleLabelAction): FlagReportState => {
      const makeState = (label_values: LabelValue[]): FlagReportState => {
        const submittable = label_values.map(({ checked }) => checked).some(Boolean);
        return { label_values, submittable };
      };

      switch (action.type) {
        case "load_labels":
          return makeState(
            action.labels.map((label) => {
              return { label, checked: false, value: 1 };
            })
          );
        case "toggle_label": {
          const values_copy = state.label_values.slice();
          values_copy[action.label_index].checked = action.check;
          return makeState(values_copy);
        }
        case "update_value": {
          const values_copy = state.label_values.slice();
          values_copy[action.label_index].value = action.value;
          return makeState(values_copy);
        }
      }
    },
    { label_values: [], submittable: false }
  );
  const [isEditing, setIsEditing] = useBoolean();
  const backgroundColor = useColorModeValue("gray.200", "gray.700");

  const { data, isLoading } = useSWR("/api/valid_labels", fetcher);
  useEffect(() => {
    if (isLoading) {
      return;
    }
    const { valid_labels } = data;
    updateReport({ type: "load_labels", labels: valid_labels });
  }, [data, isLoading]);

  const { trigger } = useSWRMutation("/api/set_label", poster, {
    onSuccess: () => {
      setIsEditing.off();
    },
  });

  const submitResponse = () => {
    const label_map: Map<string, number> = new Map();
    report.label_values.forEach(({ label, checked, value }) => {
      if (checked) {
        label_map.set(label.name, value);
      }
    });
    trigger({
      message_id: props.message.id,
      label_map: Object.fromEntries(label_map),
      text: props.message.text,
    });
  };

  const handleCheckboxState = (checked, label_index) => {
    updateReport({ type: "toggle_label", label_index, check: checked });
  };
  const handleSliderState = (value, label_index) => {
    updateReport({ type: "update_value", label_index, value });
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
        <Tooltip label="Report" bg="red.500">
          <div>
            <PopoverTrigger>
              <Button h="full" bg={backgroundColor}>
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
          {report.label_values.map(({ label, checked, value }, i) => (
            <FlagCheckbox
              label={label}
              key={i}
              idx={i}
              checked={checked}
              sliderValue={value}
              checkboxHandler={handleCheckboxState}
              sliderHandler={handleSliderState}
            />
          ))}
          <Flex justify="center">
            <Button
              isDisabled={!report.submittable}
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

interface FlagCheckboxProps {
  label: Label;
  idx: number;
  checked: boolean;
  sliderValue: number;
  checkboxHandler: (newVal: boolean, idx: number) => void;
  sliderHandler: (newVal: number, idx: number) => void;
}

export function FlagCheckbox(props: FlagCheckboxProps): JSX.Element {
  let AdditionalExplanation = null;
  if (props.label.help_text) {
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
        isChecked={props.checked}
        onChange={(e) => {
          props.checkboxHandler(e.target.checked, props.idx);
        }}
      />
      <label className="text-sm form-check-label" htmlFor={id}>
        <span className={labelTextClass}>{props.label.display_text}</span>
        {AdditionalExplanation}
      </label>
      <Spacer />
      <div
        onClick={() => {
          if (!props.checked) {
            props.checkboxHandler(true, props.idx);
          }
        }}
      >
        <Slider
          width="100px"
          isDisabled={!props.checked}
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
      </div>
    </Flex>
  );
}
