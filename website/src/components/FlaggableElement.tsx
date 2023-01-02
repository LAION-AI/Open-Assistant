import {
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
  Spacer,
  useBoolean,
} from "@chakra-ui/react";
import { FlagIcon, QuestionMarkCircleIcon } from "@heroicons/react/20/solid";
import { useState } from "react";
import poster from "src/lib/poster";
import useSWRMutation from "swr/mutation";

export const FlaggableElement = (props) => {
  const [isEditing, setIsEditing] = useBoolean();
  const { trigger } = useSWRMutation("/api/v1/text_labels", poster, {
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
    trigger({ post_id: props.post_id, label_map: Object.fromEntries(label_map), text: props.text });
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
      <div className="inline-block float-left">
        <PopoverAnchor>{props.children}</PopoverAnchor>
        <PopoverTrigger>
          <Button color="transparent">
            <FlagIcon
              className="h-5 w-5 ml-3 align-center text-gray-400 group-hover:text-gray-500"
              aria-hidden="true"
            />
          </Button>
        </PopoverTrigger>
      </div>

      <PopoverContent width="fit-content">
        <PopoverArrow />
        <PopoverCloseButton />
        <div className="flex mt-3 ">
          <PopoverBody>
            <ul>
              {TEXT_LABEL_FLAGS.map((option, i) => {
                return (
                  <FlagCheckboxLi
                    option={option}
                    key={i}
                    idx={i}
                    checkboxValues={checkboxValues}
                    sliderValues={sliderValues}
                    checkboxHandler={handleCheckboxState}
                    sliderHandler={handleSliderState}
                  ></FlagCheckboxLi>
                );
              })}
            </ul>
            <div className="flex justify-center ml-auto">
              <Button
                isDisabled={
                  !checkboxValues.reduce((all, current) => {
                    return all | current;
                  }, false)
                }
                onClick={() => submitResponse()}
                className="bg-indigo-600 text-black hover:bg-indigo-700"
              >
                Report
              </Button>
            </div>
          </PopoverBody>
        </div>
      </PopoverContent>
    </Popover>
  );
};
function FlagCheckboxLi(props: {
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

  return (
    <li>
      <Flex>
        <Checkbox
          onChange={(e) => {
            props.checkboxHandler(e.target.checked, props.idx);
          }}
        />
        <label
          className=" ml-1 mr-1 text-sm form-check-label  hover:cursor-pointer"
          htmlFor={props.option.attributeName}
        >
          <span className="text-gray-800 hover:text-blue-700 float-left">{props.option.labelText}</span>
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
    </li>
  );
}
interface textFlagLabels {
  attributeName: string;
  labelText: string;
  additionalExplanation?: string;
}
const TEXT_LABEL_FLAGS: textFlagLabels[] = [
  // For the time being this list is configured on the FE.
  // In the future it may be provided by the API.
  {
    attributeName: "fails_task",
    labelText: "Fails to follow the correct instruction / task",
    additionalExplanation: "__TODO__",
  },
  {
    attributeName: "not_customer_assistant_appropriate",
    labelText: "Inappropriate for customer assistant",
    additionalExplanation: "__TODO__",
  },
  {
    attributeName: "contains_sexual_content",
    labelText: "Contains sexual content",
  },
  {
    attributeName: "contains_violent_content",
    labelText: "Contains violent content",
  },
  {
    attributeName: "encourages_violence",
    labelText: "Encourages or fails to discourage violence/abuse/terrorism/self-harm",
  },
  {
    attributeName: "denigrates_a_protected_class",
    labelText: "Denigrates a protected class",
  },
  {
    attributeName: "gives_harmful_advice",
    labelText: "Fails to follow the correct instruction / task",
    additionalExplanation:
      "The advice given in the output is harmful or counter-productive. This may be in addition to, but is distinct from the question about encouraging violence/abuse/terrorism/self-harm.",
  },
  {
    attributeName: "expresses_moral_judgement",
    labelText: "Expresses moral judgement",
  },
];
