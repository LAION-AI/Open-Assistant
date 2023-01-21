import { Box, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import { useState } from "react";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";

export const CreateTask = ({
  task,
  taskType,
  isEditable,
  isDisabled,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<{ text: string }>) => {
  const cardColor = useColorModeValue("gray.50", "gray.800");
  const titleColor = useColorModeValue("gray.800", "gray.300");

  const [inputText, setInputText] = useState("");
  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = event.target.value;
    const isTextBlank = !text || /^\s*$/.test(text) ? true : false;
    onReplyChanged({ text });
    if (!isTextBlank) {
      onValidityChanged("VALID");
      setInputText(text);
    } else {
      onValidityChanged("INVALID");
      setInputText("");
    }
  };

  return (
    <div data-cy="task" data-task-type="create-task">
      <TwoColumnsWithCards>
        <>
          <TaskHeader taskType={taskType} />
          {task.conversation ? (
            <Box mt="4" borderRadius="lg" bg={cardColor} className="p-3 sm:p-6">
              <MessageTable messages={task.conversation.messages} />
            </Box>
          ) : null}
        </>
        <>
          <Stack spacing="4">
            <Text fontSize="xl" fontWeight="bold" color={titleColor}>
              {taskType.instruction}
            </Text>
            <TrackedTextarea
              text={inputText}
              onTextChange={textChangeHandler}
              thresholds={{ low: 20, medium: 40, goal: 50 }}
              textareaProps={{ placeholder: "Write your prompt here...", isDisabled, isReadOnly: !isEditable }}
            />
          </Stack>
        </>
      </TwoColumnsWithCards>
    </div>
  );
};
