import axios from "axios";
import Head from "next/head";
import Image from "next/image";
import { useSession, signIn, signOut } from "next-auth/react";
import { useEffect, useRef, useState } from "react";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const fetcher = (url) => axios.get(url).then((res) => res.data);

async function sendRequest(url, { arg }) {
  return fetch(url, {
    method: "POST",
    body: JSON.stringify(arg),
  });
}

export default function NewPage() {
  const responseEl = useRef(null);
  const {
    data: registeredTask,
    errors,
    isLoading,
  } = useSWRImmutable("/api/new_task", fetcher);
  const { trigger, isMutating } = useSWRMutation(
    "/api/update_task",
    sendRequest
  );

  const submitResponse = () => {
    trigger({
      id: registeredTask.id,
      rating: responseEl.current.value,
    });
  };
  if (isLoading) {
    return <div>Loading</div>;
  }

  return (
    <div>
      <div>{registeredTask.id}</div>
      <div>{registeredTask.task.type}</div>
      <div>{registeredTask.task.text}</div>
      <div>{registeredTask.task.summary}</div>
      <div>
        {registeredTask.task.scale.min} to {registeredTask.task.scale.max}
      </div>
      <input type="text" ref={responseEl} />
      <button onClick={submitResponse}>Submit Response</button>
    </div>
  );
}
