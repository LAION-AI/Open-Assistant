export const TaskInfo = ({ id, output }: { id: string; output: string }) => {
  return (
    <div className="grid grid-cols-[min-content_auto] gap-x-2">
      <b>Prompt</b>
      <span data-cy="task-id">{id}</span>
      <b>Output</b>
      <span>{output}</span>
    </div>
  );
};
