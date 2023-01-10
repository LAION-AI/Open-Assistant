import { Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useEffect, useId, useState } from "react";
import { MessageView } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskInfo } from "src/components/Tasks/TaskTypes";
import { TaskType } from "src/types/Task";
import { colors } from "styles/Theme/colors";

export interface LabelTaskProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  tasks: any[];
  taskType: TaskInfo;
  trigger: (update: {
    id: string;
    update_type: string;
    content: { text: string; labels: { [k: string]: number }; message_id: string };
  }) => void;
  onSkipTask: (task: { id: string }, reason: string) => void;
  onNextTask: () => void;
  mainBgClasses: string;
}
export const LabelTask = ({ tasks, taskType, trigger, onSkipTask, onNextTask, mainBgClasses }: LabelTaskProps) => {
  const task = tasks[0].task;
  const valid_labels = tasks[0].valid_labels;

  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const submitResponse = (task: { id: string; reply: string; message_id: string }) => {
    console.assert(valid_labels.length === sliderValues.length);
    const labels = Object.fromEntries(valid_labels.valid_labels.map((label, i) => [label.name, sliderValues[i]]));
    trigger({
      id: task.id,
      update_type: "text_labels",
      // TODO: task isn't working, changed to tasks[0].task as a temporary workaround
      content: { labels, text: tasks[0].task.reply, message_id: tasks[0].task.message_id },
    });
  };

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">{taskType.label}</h5>
          <p className="text-lg py-1">{taskType.overview}</p>

          {task.conversation ? (
            <MessageTable
              messages={[
                ...(task.conversation ? task.conversation.messages : []),
                {
                  text: task.reply,
                  is_assistant: task.type === TaskType.label_assistant_reply,
                  message_id: task.message_id,
                },
              ]}
              valid_labels={valid_labels}
            />
          ) : (
            <MessageView text={task.prompt} is_assistant={false} message_id={task.message_id} />
          )}
        </>
        <LabelSliderGroup labelIDs={task.valid_labels} onChange={setSliderValues} />
      </TwoColumnsWithCards>

      <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkipTask={onSkipTask} onNextTask={onNextTask} />
    </div>
  );
};

// TODO: consolidate with FlaggableElement
interface LabelSliderGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
}

export const LabelSliderGroup = ({ labelIDs, onChange }: LabelSliderGroupProps) => {
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
