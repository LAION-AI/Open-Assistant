import { Box, Flex, Text, useColorModeValue } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { MessageView } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { LabelInputGroup } from "src/components/Survey/LabelInputGroup";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { TaskType } from "src/types/Task";

export const LabelTask = ({
  task,
  taskType,
  isEditable,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<{ text: string; labels: Record<string, number>; message_id: string }>) => {
  const [sliderValues, setSliderValues] = useState<number[]>(new Array(task.valid_labels.length).fill(null));

  useEffect(() => {
    console.assert(task.valid_labels.length === sliderValues.length);
    const labels = Object.fromEntries(task.valid_labels.map((label, i) => [label, sliderValues[i]]));
    onReplyChanged({ labels, text: task.reply || task.prompt, message_id: task.message_id });
    onValidityChanged(sliderValues.every((value) => value !== null) ? "VALID" : "INVALID");
  }, [task, sliderValues, onReplyChanged, onValidityChanged]);

  const cardColor = useColorModeValue("gray.50", "gray.800");

  return (
    <div data-cy="task" data-task-type="label-task">
      <TwoColumnsWithCards>
        <>
          <TaskHeader taskType={taskType} />
          {task.conversation ? (
            <Box mt="4" p={[4, 6]} borderRadius="lg" bg={cardColor}>
              <MessageTable
                messages={[
                  ...(task.conversation?.messages ?? []),
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
        <Flex direction="column" alignItems="stretch">
          <Text>The highlighted message:</Text>
          <LabelInputGroup
            simple={task.mode === "simple"}
            labelIDs={task.valid_labels}
            isEditable={isEditable}
            onChange={setSliderValues}
          />
        </Flex>
      </TwoColumnsWithCards>
    </div>
  );
};
