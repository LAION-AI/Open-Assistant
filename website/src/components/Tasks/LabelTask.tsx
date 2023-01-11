import { Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useEffect, useId, useState } from "react";
import { MessageView } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskType } from "src/types/Task";
import { colors } from "styles/Theme/colors";

export const LabelTask = ({
  task,
  taskType,
  onReplyChanged,
}: TaskSurveyProps<{ text: string; labels: { [k: string]: number }; message_id: string }>) => {
  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const valid_labels = task.valid_labels;

  useEffect(() => {
    onReplyChanged({ content: { labels: {}, text: task.reply, message_id: task.message_id }, state: "DEFAULT" });
  }, [task.reply, task.message_id, onReplyChanged]);

  const onSliderChange = (values: number[]) => {
    console.assert(valid_labels.length === sliderValues.length);
    const labels = Object.fromEntries(valid_labels.map((label, i) => [label, sliderValues[i]]));
    onReplyChanged({ content: { labels, text: task.reply, message_id: task.message_id }, state: "VALID" });
    setSliderValues(values);
  };

  return (
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
          />
        ) : (
          <MessageView text={task.prompt} is_assistant={false} message_id={task.message_id} />
        )}
      </>
      <LabelSliderGroup labelIDs={task.valid_labels} onChange={onSliderChange} />
    </TwoColumnsWithCards>
  );
};

// TODO: consolidate with FlaggableElement
interface LabelSliderGroupProps {
  labelIDs: Array<string>;
  onChange: (sliderValues: number[]) => unknown;
}

export const LabelSliderGroup = ({ labelIDs, onChange }: LabelSliderGroupProps) => {
  const [sliderValues, setSliderValues] = useState<number[]>(Array.from({ length: labelIDs.length }).map(() => 0));

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
            onChange(sliderValues);
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
