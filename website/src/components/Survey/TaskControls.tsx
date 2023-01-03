import { useColorMode } from "@chakra-ui/react";
import { Flex } from "@chakra-ui/react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";

interface TaskControlsProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  tasks: any[];
  className?: string;
  onSubmitResponse: (task: { id: string }) => void;
  onSkip: () => void;
}

export const TaskControls = (props: TaskControlsProps) => {
  const extraClases = props.className || "";
  const { colorMode } = useColorMode();

  const baseClasses = "flex flex-row justify-items-stretch mb-8 p-4 rounded-lg max-w-7xl mx-auto";
  const taskControlClases =
    colorMode === "light"
      ? `${baseClasses} bg-white text-gray-800 shadow-lg ${extraClases}`
      : `${baseClasses} bg-slate-800 text-slate-400 shadow-xl ring-1 ring-white/10 ring-inset ${extraClases}`;

  const endTask = props.tasks[props.tasks.length - 1];
  return (
    <section className={taskControlClases}>
      <TaskInfo id={props.tasks[0].id} output="Submit your answer" />
      <Flex justify="center" ml="auto" gap={2}>
        <SkipButton>Skip</SkipButton>
        {endTask.task.type !== "task_done" ? (
          <SubmitButton data-cy="submit" onClick={() => props.onSubmitResponse(props.tasks[0])}>
            Submit
          </SubmitButton>
        ) : (
          <SubmitButton data-cy="next-task" onClick={props.onSkip}>
            Next Task
          </SubmitButton>
        )}
      </Flex>
    </section>
  );
};
