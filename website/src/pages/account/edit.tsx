import React, { useState } from "react";
import { useSession } from "next-auth/react";
import { Button, Input, InputGroup, Stack } from "@chakra-ui/react";
import Head from "next/head";
import Router from "next/router";

export default function Account() {
  const { data: session } = useSession();
  const [username, setUsername] = useState("");
  const updateUser = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    try {
      const body = { username };
      await fetch("/api/username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      await Router.push("/account");
    } catch (error) {
      console.error(error);
    }
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
        <p>{session.user.name || "No username"}</p>
        <form onSubmit={updateUser}>
          <InputGroup>
            <Input
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Edit Username"
              type="text"
              value={username}
            ></Input>
            <Button disabled={!username} type="submit" value="Change">
              Submit
            </Button>
          </InputGroup>
        </form>
        <p>{session.user.email}</p>
      </main>
    </>
  );
}
