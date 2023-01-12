import { Box, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import { useEffect } from "react";
import { MessageTable } from "src/components/Messages/MessageTable";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskSurveyProps } from "src/components/Tasks/Task";

export const EvaluateTask = ({ task, onReplyChanged }: TaskSurveyProps<{ ranking: number[] }>) => {
  const cardColor = useColorModeValue("gray.100", "gray.700");
  const titleColor = useColorModeValue("gray.800", "gray.300");
  const labelColor = useColorModeValue("gray.600", "gray.400");

  let messages = [];
  if (task.conversation) {
    messages = task.conversation.messages;
    messages = messages.map((message, index) => ({ ...message, id: index }));
  }

  useEffect(() => {
    const conversationMsgs = task.conversation ? task.conversation.messages : [];
    const defaultRanking = conversationMsgs.map((message, index) => index);
    onReplyChanged({
      content: { ranking: defaultRanking },
      state: "DEFAULT",
    });
  }, [task.conversation, onReplyChanged]);

  const onRank = (newRanking: number[]) => {
    onReplyChanged({ content: { ranking: newRanking }, state: "VALID" });
  };

  const sortables = task.replies ? "replies" : "prompts";

  return (
    <div data-cy="task" data-task-type="evaluate-task">
      <Box mb="4">
        <SurveyCard>
          <Stack spacing="1">
            <Text fontSize="xl" fontWeight="bold" color={titleColor}>
              Instructions
            </Text>
            <Text fontSize="md" color={labelColor}>
              Given the following {sortables}, sort them from best to worst, best being first, worst being last.
            </Text>
          </Stack>
          <Box mt="4" p="6" borderRadius="lg" bg={cardColor}>
            <MessageTable messages={messages} />
          </Box>
          <Sortable items={task[sortables]} onChange={onRank} className="my-8" />
        </SurveyCard>
      </Box>
    </div>
  );
};
