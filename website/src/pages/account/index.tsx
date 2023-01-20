import { Button } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useSession } from "next-auth/react";
import React from "react";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

export default function Account() {
  const { data: session } = useSession();

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
      <div className="oa-basic-theme">
        <main className="h-3/4 z-0 flex flex-col items-center justify-center">
          <p>{session.user.name || "No username"}</p>
          <Button>
            <Link href="/account/edit">Edit Username</Link>
          </Button>
          <p>{session.user.email}</p>
        </main>
      </div>
    </>
  );
}
