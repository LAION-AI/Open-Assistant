import { Box, Grid, Slider, SliderFilledTrack, SliderThumb, SliderTrack } from "@chakra-ui/react";
import { Text, useColorMode, useColorModeValue } from "@chakra-ui/react";
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
  const valid_labels = task.valid_labels;
  const [sliderValues, setSliderValues] = useState<number[]>(new Array(valid_labels.length).fill(0));

  useEffect(() => {
    onReplyChanged({ content: { labels: {}, text: task.reply, message_id: task.message_id }, state: "DEFAULT" });
  }, [task.reply, task.message_id, onReplyChanged]);

  const onSliderChange = (values: number[]) => {
    console.assert(valid_labels.length === sliderValues.length);
    const labels = Object.fromEntries(valid_labels.map((label, i) => [label, sliderValues[i]]));
    onReplyChanged({
      content: { labels, text: task.reply || task.prompt, message_id: task.message_id },
      state: "VALID",
    });
    setSliderValues(values);
  };

  const cardColor = useColorModeValue("gray.100", "gray.700");
  const titleColor = useColorModeValue("gray.800", "gray.300");
  const labelColor = useColorModeValue("gray.600", "gray.400");

  return (
    <div data-cy="task" data-task-type="label-task">
      <TwoColumnsWithCards>
        <>
          <Text fontSize="xl" fontWeight="bold" color={titleColor}>
            {taskType.label}
          </Text>
          <Text fontSize="md" color={labelColor}>
            {taskType.overview}
          </Text>

          {task.conversation ? (
            <Box mt="4" p="6" borderRadius="lg" bg={cardColor}>
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
            </Box>
          ) : (
            <Box mt="4">
              <MessageView text={task.prompt} is_assistant={false} message_id={task.message_id} />
            </Box>
          )}
        </>
        <LabelSliderGroup labelIDs={task.valid_labels} onChange={onSliderChange} />
      </TwoColumnsWithCards>
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
