import {
  Box,
  Button,
  Checkbox,
  Flex,
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
  Tooltip,
  useBoolean,
  useColorMode,
  useColorModeValue,
  useId,
} from "@chakra-ui/react";
import { QuestionMarkCircleIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { AlertCircle } from "lucide-react";
import { useEffect, useReducer } from "react";
import { get, post } from "src/lib/api";
import { colors } from "src/styles/Theme/colors";
import { Message } from "src/types/Conversation";
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

  const { data, isLoading } = useSWR("/api/valid_labels", get);
  useEffect(() => {
    if (isLoading) {
      return;
    }
    if (!data) {
      updateReport({ type: "load_labels", labels: [] });
      return;
    }
    const { valid_labels } = data;
    updateReport({ type: "load_labels", labels: valid_labels });
  }, [data, isLoading]);

  const { trigger } = useSWRMutation("/api/set_label", post, {
    onSuccess: setIsEditing.off,
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
      <Box display="flex" alignItems="center" flexDirection={["column", "row"]} gap="2">
        <PopoverAnchor>{props.children}</PopoverAnchor>

        <Tooltip label="Report" bg="red.500" aria-label="A tooltip">
          <Box>
            <PopoverTrigger>
              <Box as="button" display="flex" alignItems="center" justifyContent="center" borderRadius="full" p="1">
                <AlertCircle size="20" className="text-red-400" aria-hidden="true" />
              </Box>
            </PopoverTrigger>
          </Box>
        </Tooltip>
      </Box>

      <PopoverContent width="auto" p="3" m="4" maxWidth="calc(100vw - 2rem)">
        <PopoverArrow />
        <Box className="relative h-4">
          <PopoverCloseButton />
        </Box>
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
      <a href="#" className="text-sm inline group leading-4">
        <QuestionMarkCircleIcon
          className="h-5 w-5 ml-1 text-gray-400 group-hover:text-gray-500 inline"
          aria-hidden="true"
        />
      </a>
    );
  }

  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass =
    colorMode === "light"
      ? `text-${colors.light.text} hover:text-blue-700`
      : `text-${colors.dark.text} hover:text-blue-400`;

  return (
    <Flex gap="4" justifyContent="space-between" className="my-2">
      <div className="flex items-start align-middle">
        <Checkbox
          id={id}
          isChecked={props.checked}
          onChange={(e) => {
            props.checkboxHandler(e.target.checked, props.idx);
          }}
        />
        <label
          className={clsx(
            "text-sm form-check-label ml-2 break-all inline align-middle first-line:leading-4",
            labelTextClass
          )}
          htmlFor={id}
        >
          {props.label.display_text}
          {AdditionalExplanation}
        </label>
      </div>
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
