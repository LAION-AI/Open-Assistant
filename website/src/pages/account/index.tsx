import { Button } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React, { useState } from "react";

export default function Account() {
  const { data: session } = useSession();
  const [username, setUsername] = useState("null");

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleUpdate = async () => {
    const response = await fetch("../api/update", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username }),
    });
    const { name } = await response.json();
    setUsername(name);
  };

  if (!session) {
    return;
  }
  return (
    <>
      <Head>
        <title>Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <main className="h-3/4 z-0 bg-white flex flex-col items-center justify-center">
        <p>{username}</p>
        <Button>
          <Link href="/account/edit">Edit Username</Link>
        </Button>
        <p>{session.user.email}</p>
      </main>
    </>
  );
}
