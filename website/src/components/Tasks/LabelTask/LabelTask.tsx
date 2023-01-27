import { Box, Button, Flex, HStack, Text, useColorModeValue } from "@chakra-ui/react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { MessageView } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { LabelInputGroup } from "src/components/Survey/LabelInputGroup";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { Message } from "src/types/Conversation";
import { TaskType } from "src/types/Task";

export const LabelTask = ({
  task,
  taskType,
  isEditable,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<{ text: string; labels: Record<string, number>; message_id: string }>) => {
  const { i18n } = useTranslation();
  const [sliderValues, setSliderValues] = useState<number[]>(new Array(task.valid_labels.length).fill(null));

  useEffect(() => {
    console.assert(task.valid_labels.length === sliderValues.length);
    const labels = Object.fromEntries(task.valid_labels.map((label, i) => [label, sliderValues[i]]));
    onReplyChanged({ labels, text: task.reply || task.prompt, message_id: task.message_id });
    onValidityChanged(sliderValues.every((value) => value !== null) ? "VALID" : "INVALID");
  }, [task, sliderValues, onReplyChanged, onValidityChanged]);

  const cardColor = useColorModeValue("gray.50", "gray.800");
  const isSpamTask = task.mode === "simple" && task.valid_labels.length === 1 && task.valid_labels[0] === "spam";

  // TODO: remove as soon as the backend delivers
  // real information about the current message
  const additionMessage: Message = useMemo(
    () => ({
      text: task.reply,
      is_assistant: task.type === TaskType.label_assistant_reply,
      message_id: task.message_id,
      created_date: new Date().toISOString(),
      emojis: {},
      user_emojis: [],
      id: "dummy",
      lang: i18n.language,
      parent_id: "dummy",
    }),
    [task.reply, task.type, task.message_id, i18n.language]
  );

  return (
    <div data-cy="task" data-task-type={isSpamTask ? "spam-task" : "label-task"}>
      <TwoColumnsWithCards>
        <>
          <TaskHeader taskType={taskType} />
          {task.conversation ? (
            <Box mt="4" p={[4, 6]} borderRadius="lg" bg={cardColor}>
              <MessageTable messages={[...(task.conversation?.messages ?? []), additionMessage]} highlightLastMessage />
            </Box>
          ) : (
            <Box mt="4">
              <MessageView text={task.prompt} is_assistant={false} id={task.message_id} emojis={{}} user_emojis={[]} />
            </Box>
          )}
        </>
        {isSpamTask ? (
          <SpamTaskInput
            value={sliderValues[0]}
            onChange={(value) => setSliderValues([value])}
            isEditable={isEditable}
          />
        ) : (
          <Flex direction="column" alignItems="stretch">
            <Text>The highlighted message:</Text>
            <LabelInputGroup labelIDs={task.valid_labels} isEditable={isEditable} onChange={setSliderValues} />
          </Flex>
        )}
      </TwoColumnsWithCards>
    </div>
  );
};

const SpamTaskInput = ({
  isEditable,
  value,
  onChange,
}: {
  isEditable: boolean;
  value: number;
  onChange: (number) => void;
}) => {
  return (
    <HStack>
      <Text>Is the highlighted message spam?</Text>
      <Button
        data-cy="spam-button"
        isDisabled={!isEditable}
        colorScheme={value === 1 ? "blue" : undefined}
        onClick={() => onChange(1)}
      >
        Yes
      </Button>
      <Button
        data-cy="not-spam-button"
        isDisabled={!isEditable}
        colorScheme={value === 0 ? "blue" : undefined}
        onClick={() => onChange(0)}
      >
        No
      </Button>
    </HStack>
  );
};
