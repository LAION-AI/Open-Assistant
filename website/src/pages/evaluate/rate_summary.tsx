import { Flex, Textarea } from "@chakra-ui/react";
import { QuestionMarkCircleIcon } from "@heroicons/react/20/solid";
import Head from "next/head";
import { useState } from "react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import RatingRadioGroup from "src/components/RatingRadioGroup";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TwoColumns } from "src/components/TwoColumns";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const RateSummary = () => {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);
  const [rating, setRating] = useState(0);

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading, mutate } = useSWRImmutable("/api/new_task/rate_summary", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  // Every time we submit an answer to the latest task, let the backend handle
  // all the interactions then add the resulting task to the queue.  This ends
  // when we hit the done task.
  const { trigger, isMutating } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      // This is the more efficient way to update a react state array.
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  // Trigger a mutation that updates the current task.  We should probably
  // signal somewhere that this interaction is being processed.
  const submitResponse = (t) => {
    trigger({
      id: t.id,
      update_type: "message_rating",
      content: {
        rating: rating,
      },
    });
  };

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">No tasks found...</div>;
  }

  const endTask = tasks[tasks.length - 1];
  return (
    <>
      <Head>
        <title>Rate A Summary</title>
        <meta name="description" content="Rate a proposed story summary." />
      </Head>
      <main className="p-6 bg-slate-100 text-gray-800">
        <TwoColumns>
          <>
            <h5 className="text-lg font-semibold mb-4">Instruction</h5>
            <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">{tasks[0].task.full_text}</div>
          </>

          <section className="grid grid-row-[auto] gap-3">
            <h5 className="text-lg font-semibold">Output</h5>
            <p className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">{tasks[0].task.summary}</p>
            <h3 className="text-lg text-center font-medium leading-6 text-gray-900">Rating</h3>
            <p className="text-center text-sm text-gray-500">
              ({tasks[0].task.scale.min} = worst, {tasks[0].task.scale.max} = best)
            </p>
            <div className="m-auto">
              <RatingRadioGroup min={tasks[0].task.scale.min} max={tasks[0].task.scale.max} onChange={setRating} />
            </div>
            <ul>
              {ANNOTATION_FLAGS.map((option, i) => (
                <AnnotationCheckboxLi option={option} key={i} />
              ))}
            </ul>
            <Textarea name="notes" placeholder="Optional notes" />
          </section>
        </TwoColumns>

        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
          <TaskInfo id={tasks[0].id} output="Submit your answer" />

          <Flex justify="center" ml="auto" gap={2}>
            <SkipButton>Skip</SkipButton>
            {endTask.task.type !== "task_done" ? (
              <SubmitButton onClick={() => submitResponse(tasks[0])}>Submit</SubmitButton>
            ) : (
              <SubmitButton onClick={mutate}>Next Task</SubmitButton>
            )}
          </Flex>
        </section>
      </main>
    </>
  );
};

export default RateSummary;

function AnnotationCheckboxLi(props: { option: annotationBool }): JSX.Element {
  let AdditionalExplanation = null;
  if (props.option.additionalExplanation) {
    AdditionalExplanation = (
      <a href="#" className="group flex items-center space-x-2.5 text-sm ">
        <QuestionMarkCircleIcon className="h-5 w-5 ml-3 text-gray-400 group-hover:text-gray-500" aria-hidden="true" />
      </a>
    );
  }

  return (
    <li className="form-check flex mb-1">
      <input
        className="form-check-input appearance-none h-4 w-4 border border-gray-300 rounded-sm bg-white checked:bg-blue-600 checked:border-blue-600 focus:outline-none transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain float-left mr-2 cursor-pointer"
        type="checkbox"
        value=""
        id={props.option.attributeName}
      />
      <label className="flex ml-1 form-check-label  hover:cursor-pointer" htmlFor={props.option.attributeName}>
        <span className="text-gray-800 hover:text-blue-700">{props.option.labelText}</span>
        {AdditionalExplanation}
      </label>
    </li>
  );
}

interface annotationBool {
  attributeName: string;
  labelText: string;
  additionalExplanation?: string;
}

const ANNOTATION_FLAGS: annotationBool[] = [
  // For the time being this list is configured on the FE.
  // In the future it may be provided by the API.
  {
    attributeName: "fails_task",
    labelText: "Fails to follow the correct instruction / task",
    additionalExplanation: "__TODO__",
  },
  {
    attributeName: "not_customer_assistant_appropriate",
    labelText: "Inappropriate for customer assistant",
    additionalExplanation: "__TODO__",
  },
  {
    attributeName: "contains_sexual_content",
    labelText: "Contains sexual content",
  },
  {
    attributeName: "contains_violent_content",
    labelText: "Contains violent content",
  },
  {
    attributeName: "encourages_violence",
    labelText: "Encourages or fails to discourage violence/abuse/terrorism/self-harm",
  },
  {
    attributeName: "denigrates_a_protected_class",
    labelText: "Denigrates a protected class",
  },
  {
    attributeName: "gives_harmful_advice",
    labelText: "Fails to follow the correct instruction / task",
    additionalExplanation:
      "The advice given in the output is harmful or counter-productive. This may be in addition to, but is distinct from the question about encouraging violence/abuse/terrorism/self-harm.",
  },
  {
    attributeName: "expresses_moral_judgement",
    labelText: "Expresses moral judgement",
  },
];
