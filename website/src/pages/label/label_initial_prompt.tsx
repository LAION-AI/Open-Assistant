import { Container, Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useEffect, useId, useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { MessageView } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { LabelInitialPromptTask, LabelInitialPromptTaskResponse, useLabelingTask } from "src/hooks/useLabelingTask";
import { colors } from "styles/Theme/colors";

const LabelInitialPrompt = () => {
  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const { tasks, isLoading, submit, reset } = useLabelingTask<LabelInitialPromptTask>({
    taskApiEndpoint: "label_initial_prompt",
  });

  const submitResponse = ({ id, task }: LabelInitialPromptTaskResponse) => {
    const labels = task.valid_labels.reduce((obj, label, i) => {
      obj[label] = sliderValues[i].toString();
      return obj;
    }, {} as Record<string, string>);

    submit(id, task.message_id, task.prompt, labels);
  };

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <Container className="p-6 text-center text-gray-800">No tasks found...</Container>;
  }

  const task = tasks[0].task;

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">Label Initial Prompt</h5>
          <p className="text-lg py-1">Provide labels for the following prompt</p>
          <MessageView text={task.prompt} is_assistant />
        </>
        <CheckboxSliderGroup labelIDs={task.valid_labels} onChange={setSliderValues} />
      </TwoColumnsWithCards>
      <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkip={reset} />
    </div>
  );
};

export default LabelInitialPrompt;

// TODO: consolidate with FlaggableElement

interface CheckboxSliderGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
}

const CheckboxSliderGroup = ({ labelIDs, onChange }: CheckboxSliderGroupProps) => {
  const [sliderValues, setSliderValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => 0));

  useEffect(() => {
    onChange(sliderValues);
  }, [sliderValues, onChange]);

  return (
    <Grid templateColumns="auto 1fr" rowGap={1} columnGap={3}>
      {labelIDs.map((labelId, idx) => (
        <CheckboxSliderItem
          key={idx}
          labelId={labelId}
          sliderValue={sliderValues[idx]}
          sliderHandler={(sliderValue) => {
            const newState = sliderValues.slice();
            newState[idx] = sliderValue;
            setSliderValues(newState);
          }}
        />
      ))}
    </Grid>
  );
};

function CheckboxSliderItem(props: {
  labelId: string;
  sliderValue: number;
  sliderHandler: (newVal: number) => unknown;
}) {
  const id = useId();
  const { colorMode } = useColorMode();

  const labelTextClass = colorMode === "light" ? `text-${colors.light.text}` : `text-${colors.dark.text}`;

  return (
    <>
      <label className="text-sm" htmlFor={id}>
        {/* TODO: display real text instead of just the id */}
        <span className={labelTextClass}>{props.labelId}</span>
      </label>
      <Slider defaultValue={0} onChangeEnd={(val) => props.sliderHandler(val / 100)}>
        <SliderTrack>
          <SliderFilledTrack />
          <SliderThumb />
        </SliderTrack>
      </Slider>
    </>
  );
}
