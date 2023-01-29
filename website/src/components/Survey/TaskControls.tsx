import { Box, Flex, IconButton, Tooltip, useColorModeValue } from "@chakra-ui/react";
import { Edit2 } from "lucide-react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TaskStatus } from "src/components/Tasks/Task";
import { BaseTask } from "src/types/Task";

export interface TaskControlsProps {
  task: BaseTask;
  taskStatus: TaskStatus;
  onEdit: () => void;
  onReview: () => void;
  onSubmit: () => void;
  onSkip: (reason: string) => void;
}

export const TaskControls = ({ task, taskStatus, onEdit, onReview, onSubmit, onSkip }: TaskControlsProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  return (
    <Box
      width="full"
      bg={backgroundColor}
      borderRadius="xl"
      p="6"
      display="flex"
      flexDirection={["column", "row"]}
      shadow="base"
      gap="4"
    >
      <TaskInfo id={task.id} output="Submit your answer" />
      <Flex width={["full", "fit-content"]} justify="center" ml="auto" gap={2}>
        {taskStatus.mode === "EDIT" ? (
          <>
            <SkipButton onSkip={onSkip} />
            <SubmitButton
              colorScheme="blue"
              data-cy="review"
              isDisabled={taskStatus.replyValidity === "INVALID"}
              onClick={onReview}
            >
              Review
            </SubmitButton>
          </>
        ) : (
          <>
            <Tooltip label="Edit">
              <IconButton size="lg" data-cy="edit" aria-label="edit" onClick={onEdit} icon={<Edit2 size="1em" />} />
            </Tooltip>
            <SubmitButton
              colorScheme="green"
              data-cy="submit"
              isDisabled={taskStatus.mode === "SUBMITTED"}
              onClick={onSubmit}
            >
              Submit
            </SubmitButton>
          </>
        )}
      </Flex>
    </Box>
  );
};
