import { Box, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import { useState } from "react";
import { Messages } from "src/components/Messages";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";

export const CreateTask = ({ task, taskType, onReplyChanged }: TaskSurveyProps<{ text: string }>) => {
  const titleColor = useColorModeValue("gray.800", "gray.300");
  const labelColor = useColorModeValue("gray.600", "gray.400");

  const [inputText, setInputText] = useState("");

  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = event.target.value;
    onReplyChanged({ content: { text }, state: "VALID" });
    setInputText(text);
  };

  return (
    <TwoColumnsWithCards>
      <>
        <Stack spacing="1">
          <Text fontSize="xl" fontWeight="bold" color={titleColor}>
            {taskType.label}
          </Text>
          <Text fontSize="md" color={labelColor}>
            {taskType.overview}
          </Text>
        </Stack>
        {task.conversation ? (
          <Box mt="4">
            <Messages messages={task.conversation.messages} post_id={task.id} />
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
            textareaProps={{ placeholder: "Write your prompt here..." }}
          />
        </Stack>
      </>
    </TwoColumnsWithCards>
  );
};
