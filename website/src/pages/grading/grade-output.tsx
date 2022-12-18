import { QuestionMarkCircleIcon } from "@heroicons/react/20/solid";

export default function OutputDetail(): JSX.Element {
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
                  {SAMPLE_PROMPT}
                </div>
              </div>
            </div>

            {/* Output panel */}
            <div className="mt-6 lg:mt-0 rounded-lg shadow-lg h-full block bg-white">
              <div className="p-6">
                <h5 className="text-lg font-semibold mb-4">Output</h5>
                <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">
                  {SAMPLE_OUTPUT}
                </div>
              </div>
              {/* Form  wrap*/}
              <div className="p-6">
                <h3 className="text-lg text-center font-medium leading-6 text-gray-900">
                  Rating
                </h3>
                <p className="text-center mt-1 text-sm text-gray-500">
                  (1 = worst, 7 = best)
                </p>

                {/* Rating buttons */}
                <div className="flex justify-center p-6">
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    1
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    2
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    3
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    4
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    5
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center mx-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    6
                  </button>
                  <button
                    type="button"
                    className="nline-flex items-center mx-2 rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    7
                  </button>
                </div>
              </div>

              {/* Annotation checkboxes */}
              <div className="flex justify-center px-10">
                <ul>
                  {ANNOTATION_FLAGS.map((option, i) => {
                    return (
                      <AnnotationCheckboxLi
                        option={option}
                        key={i}
                      ></AnnotationCheckboxLi>
                    );
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
              <span className="ml-2">d1fb481a-e6cd-445d-9a15-8e2add854fe1</span>
            </div>
            <div>
              <span>
                <b>Output</b>
              </span>
              <span className="ml-2">a5f85b0a-e11a-472c-bc73-946fdc2a6ec2</span>
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
              className="nline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Submit
            </button>
          </div>
        </section>
      </div>
    </>
  );
}

function AnnotationCheckboxLi(props: { option: annotationBool }): JSX.Element {
  let AdditionalExplanation = null;
  if (props.option.additionalExplanation) {
    AdditionalExplanation = (
      <a href="#" className="group flex items-center space-x-2.5 text-sm ">
        <QuestionMarkCircleIcon
          className="h-5 w-5 ml-3 text-gray-400 group-hover:text-gray-500"
          aria-hidden="true"
        />
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
        <label
          className="flex ml-1 form-check-label  hover:cursor-pointer"
          htmlFor={props.option.attributeName}
        >
          <span className="text-gray-800 hover:text-blue-700">
            {props.option.labelText}
          </span>
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
    labelText:
      "Encourages or fails to discourage violence/abuse/terrorism/self-harm",
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

const SAMPLE_PROMPT =
  "Please make a list of aspects of a good pull request. Briefly describe each aspect.";

const SAMPLE_OUTPUT = `Here are some aspects of a good pull request, which you may use to help your pull requests be good contributions and get accepted:

1. Communicate:
2. Pull request size:
    * Summary
    * Fix one problem
    * Limit the scope
    * Use commits
3. Use coding conventions:
4. Perform testing:
5. Rebase onto the master branch before creating your PR
6. Respond to reviews quickly
7. Thank reviewers for their suggestions
`;
