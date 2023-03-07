import { Box, Checkbox, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, useCallback, useEffect, useState } from "react";
import { MessageConversation } from "src/components/Messages/MessageConversation";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskSurveyProps } from "src/components/Tasks/Task";
import { TaskHeader } from "src/components/Tasks/TaskHeader";
import { Message } from "src/types/Conversation";
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
  const [ranking, setRanking] = useState<number[] | null>(null);
  const [notRankable, setNotRankable] = useState(false);
  let messages: Message[] = [];
  if (task.type !== TaskType.rank_initial_prompts) {
    messages = task.conversation.messages;
  }

  useEffect(() => {
    if (ranking === null) {
      if (task.type === TaskType.rank_initial_prompts) {
        onReplyChanged({ ranking: task.prompts.map((_, idx) => idx), not_rankable: notRankable });
      } else {
        onReplyChanged({ ranking: task.replies.map((_, idx) => idx), not_rankable: notRankable });
      }
      onValidityChanged(notRankable ? "VALID" : "DEFAULT");
    } else {
      onReplyChanged({ ranking, not_rankable: notRankable });
      onValidityChanged("VALID");
    }
  }, [task, ranking, onReplyChanged, onValidityChanged, notRankable]);

  const handleNotRankableChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setNotRankable(e.target.checked);
  }, []);

  const { t } = useTranslation("tasks");
  // @notmd: I haven't test `rank_initial_prompts` type yet
  const sortableItems =
    task.type === TaskType.rank_initial_prompts ? (task.prompts as unknown as Message[]) : task.reply_messages;
  return (
    <div data-cy="task" data-task-type="evaluate-task">
      <Box mb="4">
        <SurveyCard>
          <TaskHeader taskType={taskType} />
          <Box mt="4" p="6" borderRadius="lg" bg={cardColor}>
            <MessageConversation messages={messages} highlightLastMessage />
          </Box>
          <Box mt="8">
            <Sortable
              items={sortableItems}
              isDisabled={isDisabled}
              isEditable={isEditable}
              revealSynthetic={task.reveal_synthetic}
              onChange={setRanking}
            />
            <Checkbox
              size="lg"
              mt="4"
              checked={notRankable}
              isDisabled={isDisabled || !isEditable}
              onChange={handleNotRankableChange}
            >
              {t("not_rankable")}
            </Checkbox>
          </Box>
        </SurveyCard>
      </Box>
    </div>
  );
};
