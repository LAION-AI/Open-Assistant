import { Box, useColorModeValue } from "@chakra-ui/react";
import { useEffect } from "react";
import { MessageTable } from "src/components/Messages/MessageTable";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";

export const EvaluateTask = ({
  task,
  taskType,
  isEditable,
  isDisabled,
  onReplyChanged,
}: TaskSurveyProps<{ ranking: number[] }>) => {
  const cardColor = useColorModeValue("gray.50", "gray.800");

  let messages = [];
  if (task.conversation) {
    messages = task.conversation.messages;
    messages = messages.map((message, index) => ({ ...message, id: index }));
  }

  useEffect(() => {
    const ranking = (task.replies ?? task.prompts).map((_, idx) => idx);
    onReplyChanged({ content: { ranking }, state: "DEFAULT" });
  }, [task, onReplyChanged]);

  const onRank = (newRanking: number[]) => {
    onReplyChanged({ content: { ranking: newRanking }, state: "VALID" });
  };

  const sortables = task.replies ? "replies" : "prompts";

  return (
    <div data-cy="task" data-task-type="evaluate-task">
      <Box mb="4">
        <SurveyCard>
          <TaskHeader taskType={taskType} />
          <Box mt="4" p="6" borderRadius="lg" bg={cardColor}>
            <MessageTable messages={messages} />
          </Box>
          <Sortable
            items={task[sortables]}
            isDisabled={isDisabled}
            isEditable={isEditable}
            onChange={onRank}
            className="my-8"
          />
        </SurveyCard>
      </Box>
    </div>
  );
};
