import { Button } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React from "react";

export default function Account() {
  const { data: session } = useSession();

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
        <p data-cy="username" className="hidden lg:flex">
          Username
          {/* {session.user.name || session.user.email} */}
          {/* this was working and now it's not. leaving here as a reminder for me to fix */}
        </p>
        <Button>
          <Link href="/account/edit">Edit Username</Link>
        </Button>
        <p>{session.user.email}</p>
      </main>
    </>
  );
}
