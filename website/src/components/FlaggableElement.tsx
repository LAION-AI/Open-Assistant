import poster from "src/lib/poster";
import {
  Popover,
  useBoolean,
  PopoverAnchor,
  Button,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  Checkbox,
  PopoverCloseButton,
  PopoverArrow,
  Flex,
  Spacer,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
} from "@chakra-ui/react";
import useSWRMutation from "swr/mutation";
import { QuestionMarkCircleIcon, FlagIcon } from "@heroicons/react/20/solid";
import {useState } from "react";
import { SubmitButton } from "./Buttons/Submit";

export type TextFlagProps = {
  text: string;label_map
  post_id:string;
};
type FlagRefs={
  label: string;
  value:number;
  setValue;
  isChecked:boolean;
  setChecked;
};

export const FlaggableElement = (props) => {
  const [isEditing, setIsEditing] = useBoolean();
  const [hasCheck, setHasCheck] = useBoolean();
  const { trigger, isMutating } = useSWRMutation("/api/v1/text_labels", poster, {
    onSuccess: () => {
      setIsEditing.off;
    },
  });
  
  const submitResponse = (label_data) => {
    trigger(label_data);
  };
  const label_refs:FlagRefs[]  = TEXT_LABEL_FLAGS.map((flag) =>{
    const [isChecked, setChecked] = useState(false);
    const [value, setValue] = useState(1);
    return({label:flag.attributeName, value:value, setValue:setValue, isChecked:isChecked, setChecked:setChecked});

  });
  const fetchData = () =>{
    let label_map:Map<string, number> =new Map();
    label_refs.filter((flagRef) => (flagRef.isChecked)).map((refs) =>{
      label_map.set(refs.label, refs.value)
    });
    console.log(label_map);
    return {post_id:props.post_id, label_map:Object.fromEntries(label_map), text:props.text}

  }

  return (
    <Popover isOpen={isEditing} onOpen={setIsEditing.on} onClose={setIsEditing.off} closeOnBlur={false} isLazy lazyBehavior="keepMounted">
    <div className="inline-block float-left">
    <PopoverAnchor>
      {props.children}
    </PopoverAnchor>
        <PopoverTrigger>
          <Button h="20px" >
            <FlagIcon className="h-5 w-5 ml-3 text-gray-400 group-hover:text-gray-500" aria-hidden="true" />
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
                    state={label_refs[i]}
                  ></FlagCheckboxLi>
                );
              })}           
          </ul>
          <div className="flex justify-center ml-auto">
            <Button onClick={() => submitResponse(fetchData())} className="bg-indigo-600 text-black hover:bg-indigo-700">
              Report
            </Button>
          </div>
        </PopoverBody>
        </div>
      </PopoverContent>
    </Popover>
  );
};
function FlagCheckboxLi(props: { option: textFlagLabels, state:FlagRefs}): JSX.Element {
  let AdditionalExplanation = null;
  if (props.option.additionalExplanation) {
    AdditionalExplanation = (
      <a href="#" className="group flex items-center space-x-2.5 text-sm ">
        <QuestionMarkCircleIcon className="flex h-5 w-5 ml-3 text-gray-400 group-hover:text-gray-500" aria-hidden="true" />
      </a>
    );
  }

  return (
    <>
      <li>
        <Flex>
          <Checkbox onChange={(e) => {props.state.setChecked(e.target.checked);}}/>
          <label className=" ml-1 mr-1 text-sm form-check-label  hover:cursor-pointer" htmlFor={props.option.attributeName}>
            <span className="text-gray-800 hover:text-blue-700 float-left">
              {props.option.labelText} 
            </span>
            {AdditionalExplanation}
          </label>
          <Spacer />
          <Slider width="100px" isDisabled={!props.state.isChecked} defaultValue={100} onChangeEnd={(val) => {props.state.setValue(val/100);}}>
            <SliderTrack>
              <SliderFilledTrack />
              <SliderThumb />
            </SliderTrack>
          </Slider>
        </Flex>
      </li>
    </>
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
