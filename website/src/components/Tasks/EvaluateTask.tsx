import { Box, useColorModeValue } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { MessageConversation } from "src/components/Messages/MessageConversation";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { TaskType } from "src/types/Task";
import { EvaluateTaskReply } from "src/types/TaskResponses";
import { RankTaskType } from "src/types/Tasks";

export const EvaluateTask = ({
  task,
  taskType,
  isEditable,
  isDisabled,
  onReplyChanged,
  onValidityChanged,
}: TaskSurveyProps<RankTaskType, EvaluateTaskReply>) => {
  const cardColor = useColorModeValue("gray.50", "gray.800");
  const [ranking, setRanking] = useState<number[]>(null);

  let messages = [];
  if (task.type !== TaskType.rank_initial_prompts) {
    messages = task.conversation.messages;
  }

  useEffect(() => {
    if (ranking === null) {
      if (task.type === TaskType.rank_initial_prompts) {
        onReplyChanged({ ranking: task.prompts.map((_, idx) => idx) });
      } else {
        onReplyChanged({ ranking: task.replies.map((_, idx) => idx) });
      }
      onValidityChanged("DEFAULT");
    } else {
      onReplyChanged({ ranking });
      onValidityChanged("VALID");
    }
  }, [task, ranking, onReplyChanged, onValidityChanged]);

  const sortables = task.type === TaskType.rank_initial_prompts ? "prompts" : "replies";

  return (
    <div data-cy="task" data-task-type="evaluate-task">
      <Box mb="4">
        <SurveyCard>
          <TaskHeader taskType={taskType} />
          <Box mt="4" p="6" borderRadius="lg" bg={cardColor}>
            <MessageConversation messages={messages} highlightLastMessage />
          </Box>
          <Sortable
            items={task[sortables]}
            isDisabled={isDisabled}
            isEditable={isEditable}
            onChange={setRanking}
            className="my-8"
          />
        </SurveyCard>
      </Box>
    </div>
  );
};
