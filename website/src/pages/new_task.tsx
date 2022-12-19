import Head from "next/head";
import Image from "next/image";
import { useSession, signIn, signOut } from "next-auth/react";
import { useEffect, useRef, useState } from "react";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import fetcher from "src/lib/fetcher";

/**
 * A helper function to post updates to tasks.
 * This ensures the content sent is serialized to JSON.
 */
async function sendRequest(url, { arg }) {
  return fetch(url, {
    method: "POST",
    body: JSON.stringify(arg),
  });
}

export default function NewPage() {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);

  // A quick reference to the input element.  This should be factored into the
  // component doing the actual task rendering.
  const responseEl = useRef(null);

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading } = useSWRImmutable("/api/new_task", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  // Every time we submit an answer to the latest task, let the backend handle
  // all the interactions then add the resulting task to the queue.  This ends
  // when we hit the done task.
  const { trigger, isMutating } = useSWRMutation("/api/update_task", sendRequest, {
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

  // Show something informative while loading the first task.
  if (isLoading) {
    return <div>Loading</div>;
  }

  // Iterate through each of the tasks and show it's contents, get a response to it, or show the done state.
  //
  // Right now this just works for the rating task.
  //
  // Displaying and fetching results for each task type should be factored into
  // different components that handle the presentation and response structures.
  // The results should be packaged into a single object with all the fields
  // sent to the backend.
  return (
    <div>
      {tasks.map((t) => (
        <div key={t.id}>
          <div>{t.task.type}</div>
          <div>{t.task.text}</div>
          {t.task.summary && (
            <>
              <div>{t.task.summary}</div>
              <div>
                {t.task.scale.min} to {t.task.scale.max}
              </div>
              <input type="text" ref={responseEl} />
              <button onClick={() => submitResponse(t)}>Submit Response</button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
