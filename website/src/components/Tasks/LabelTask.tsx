import { Box } from "@chakra-ui/react";
import { Text, useColorModeValue } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { MessageView } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskType } from "src/types/Task";
import { LabelSliderGroup } from "src/components/Survey/LabelSliderGroup";

export const LabelTask = ({
  task,
  taskType,
  onReplyChanged,
  isDisabled,
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
              <MessageView text={task.prompt} is_assistant={false} id={task.message_id} />
            </Box>
          )}
        </>
        <LabelSliderGroup labelIDs={task.valid_labels} isDisabled={isDisabled} onChange={onSliderChange} />
      </TwoColumnsWithCards>
    </div>
  );
};
