import { useColorMode } from "@chakra-ui/react";
import { Flex } from "@chakra-ui/react";
import clsx from "clsx";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";

export interface TaskControlsProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  tasks: any[];
  className?: string;
  onSubmitResponse: (task: { id: string }) => void;
  onSkipTask: (task: { id: string }, reason: string) => void;
  onNextTask: () => void;
}

export const TaskControls = (props: TaskControlsProps) => {
  const { colorMode } = useColorMode();
  const isLightMode = colorMode === "light";
  const endTask = props.tasks[props.tasks.length - 1];
  return (
    <section
      className={clsx(
        "flex-row justify-items-stretch mb-8 p-4 rounded-lg max-w-7xl mx-auto space-y-4 sm:space-y-0 sm:flex",
        props.className,
        {
          "bg-white text-gray-800 shadow-lg": isLightMode,
          "bg-slate-800 text-slate-400 shadow-xl ring-1 ring-white/10 ring-inset": !isLightMode,
        }
      )}
    >
      <TaskInfo id={props.tasks[0].id} output="Submit your answer" />
      <Flex justify="center" ml="auto" gap={2}>
        <SkipButton
          onSkip={(reason: string) => {
            props.onSkipTask(props.tasks[0], reason);
          }}
        />
        {endTask.task.type !== "task_done" ? (
          <SubmitButton colorScheme="blue" data-cy="submit" onClick={() => props.onSubmitResponse(props.tasks[0])}>
            Submit
          </SubmitButton>
        ) : (
          <SubmitButton colorScheme="green" data-cy="next-task" onClick={props.onNextTask}>
            Next Task
          </SubmitButton>
        )}
      </Flex>
    </section>
  );
};
