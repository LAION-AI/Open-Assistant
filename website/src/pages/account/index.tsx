import Head from "next/head";
import Link from "next/link";
import Router from "next/router";
import React, { useEffect, useState } from "react";
import { getSession, useSession } from "next-auth/react";
import { Button, Input, InputGroup, Stack } from "@chakra-ui/react";
import { Footer } from "../../components/Footer";
import { Header } from "../../components/Header";

import styles from "../styles/Home.module.css";
import { getSystemErrorName } from "util";

export default function Account() {
  const { data: session } = useSession();
  const [username, setUsername] = useState("null");

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
      <Header />
      <main className="h-3/4 z-0 bg-white flex flex-col items-center justify-center">
        <p>{username}</p>
        <Button>
          <Link href="/account/edit">Edit Username</Link>
        </Button>
        <p>{session.user.email}</p>
      </main>
      <Footer />
    </>
  );
}
