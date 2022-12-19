import { QuestionMarkCircleIcon } from "@heroicons/react/20/solid";
import { useSession, signIn, signOut } from "next-auth/react";
import { useEffect, useRef, useState } from "react";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

const GradeOutput = () => {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);

  // A quick reference to the input element.  This should be factored into the
  // component doing the actual task rendering.
  const responseEl = useRef(null);

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading } = useSWRImmutable("/api/new_task/rate_summary", fetcher, {
    onSuccess: (data) => {
      console.log(data);
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
      content: {
        rating: 2,
      },
    });
  };

  /**
   * TODO: Make this a nicer loading screen.
   */
  if (tasks.length == 0) {
    return (
      <>
        <div className=" p-6 h-full mx-auto bg-slate-100 text-gray-800"></div>
      </>
    );
  }

  return (
    <>
      <div className=" p-6 h-full mx-auto bg-slate-100 text-gray-800">
        {/* Instrunction and Output panels */}
        <section className="mb-8  lt-lg:mb-12 ">
          <div className="grid lg:gap-x-12 lg:grid-cols-2">
            {/* Instruction panel */}
            <div className="rounded-lg shadow-lg h-full block bg-white">
              <div className="p-6">
                <h5 className="text-lg font-semibold mb-4">Instruction</h5>
                <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">
                  {tasks[0].task.full_text}
                </div>
              </div>
            </div>

            {/* Output panel */}
            <div className="mt-6 lg:mt-0 rounded-lg shadow-lg h-full block bg-white">
              <div className="p-6">
                <h5 className="text-lg font-semibold mb-4">Output</h5>
                <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">
                  {tasks[0].task.summary}
                </div>
              </div>
              {/* Form  wrap*/}
              <div className="p-6">
                <h3 className="text-lg text-center font-medium leading-6 text-gray-900">Rating</h3>
                <p className="text-center mt-1 text-sm text-gray-500">(1 = worst, 7 = best)</p>

                {/* Rating buttons */}
                <div className="flex justify-center p-6">
                  <RatingButton rating={1} active={false}></RatingButton>
                  <RatingButton rating={2} active={false}></RatingButton>
                  <RatingButton rating={3} active={false}></RatingButton>
                  <RatingButton rating={4} active={false}></RatingButton>
                  <RatingButton rating={5} active={false}></RatingButton>
                  <RatingButton rating={6} active={false}></RatingButton>
                  <RatingButton rating={7} active={true}></RatingButton>
                </div>
              </div>

              {/* Annotation checkboxes */}
              <div className="flex justify-center px-10">
                <ul>
                  {ANNOTATION_FLAGS.map((option, i) => {
                    return <AnnotationCheckboxLi option={option} key={i}></AnnotationCheckboxLi>;
                  })}
                </ul>
              </div>
              <div className="flex justify-center p-6">
                <textarea
                  id="notes"
                  name="notes"
                  className="mx-1 mb-1 max-w-lg shadow-sm rounded-md focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300"
                  placeholder="Optional notes"
                  defaultValue={""}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Info & controls */}
        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
          <div className="flex flex-col justify-self-start text-gray-700">
            <div>
              <span>
                <b>Prompt</b>
              </span>
              <span className="ml-2">{tasks[0].id}</span>
            </div>
            <div>
              <span>
                <b>Output</b>
              </span>
              <span className="ml-2">{tasks.length === 2 ? tasks[1].id : "Submit your answer"}</span>
            </div>
          </div>

          {/* Skip / Submit controls */}
          <div className="flex justify-center ml-auto">
            <button
              type="button"
              className="mr-2 inline-flex items-center rounded-md border border-transparent bg-indigo-100 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Skip
            </button>
            <button
              type="button"
              onClick={() => submitResponse(tasks[0])}
              className="nline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Submit
            </button>
          </div>
        </section>
      </div>
    </>
  );
};

export default GradeOutput;

function RatingButton(props: { rating: number; active: boolean }): JSX.Element {
  const activeClasses =
    "inline-flex items-center mx-2 rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2";
  const inactiveClasses =
    "inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2";
  return (
    <button type="button" className={props.active ? activeClasses : inactiveClasses}>
      {props.rating}
    </button>
  );
}

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
    <>
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
    </>
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
