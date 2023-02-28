import { Button, Card, Flex, IconButton, Progress, Tooltip } from "@chakra-ui/react";
import { Edit2 } from "lucide-react";
import { useTranslation } from "next-i18next";
import { SubmitButton } from "src/components/Buttons/Submit";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TaskStatus } from "src/components/Tasks/Task";
import { BaseTask } from "src/types/Task";

export interface TaskControlsProps {
  task: BaseTask;
  taskStatus: TaskStatus;
  isLoading: boolean;
  isSubmitting: boolean;
  isRejecting: boolean;
  onEdit: () => void;
  onReview: () => void;
  onSubmit: () => void;
  onSkip: () => void;
}

export const TaskControls = ({
  task,
  taskStatus,
  isLoading,
  isRejecting,
  isSubmitting,
  onEdit,
  onReview,
  onSubmit,
  onSkip,
}: TaskControlsProps) => {
  const { t } = useTranslation();

  return (
    <Card>
      {isLoading && <Progress size="sm" isIndeterminate />}
      <Flex p="6" gap="4" direction={["column", "row"]}>
        <TaskInfo id={task.id} output={t("submit_your_answer")} />
        <Flex width={["full", "fit-content"]} justify="center" ml="auto" gap={2}>
          {taskStatus.mode === "EDIT" ? (
            <>
              <Button size="lg" variant="outline" onClick={onSkip} isLoading={isRejecting}>
                {t("skip")}
              </Button>
              <SubmitButton
                colorScheme="blue"
                data-cy="review"
                isDisabled={taskStatus.replyValidity === "INVALID"}
                onClick={onReview}
              >
                {t("review")}
              </SubmitButton>
            </>
          ) : (
            <>
              <Tooltip label={t("edit")}>
                <IconButton
                  size="lg"
                  data-cy="edit"
                  aria-label={t("edit")}
                  onClick={onEdit}
                  icon={<Edit2 size="1em" />}
                />
              </Tooltip>
              <SubmitButton
                colorScheme="green"
                data-cy="submit"
                isLoading={isSubmitting}
                isDisabled={taskStatus.mode === "SUBMITTED"}
                onClick={onSubmit}
              >
                {t("submit")}
              </SubmitButton>
            </>
          )}
        </Flex>
      </Flex>
    </Card>
  );
};
