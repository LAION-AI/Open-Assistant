import { useSession } from "next-auth/react";

import Head from "next/head";
import Link from "next/link";
import { Button, Input, Stack } from "@chakra-ui/react";

import { CallToAction } from "../components/CallToAction";
import { Faq } from "../components/Faq";
import { Footer } from "../components/Footer";
import { Header } from "../components/Header";
import { Hero } from "../components/Hero";

import styles from "../styles/Home.module.css";

export default function Home() {
  const { data: session } = useSession();

  if (!session) {
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
        <main className="z-0">
          <Hero />
          <CallToAction />

          <Faq />
        </main>
        <Footer />
      </>
    );
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
      <main className="h-3/4  z-0 bg-white flex items-center justify-center">
        <Button size="lg" colorScheme="blue" className="drop-shadow">
          <Link href="/grading/grade-output">Rate a prompt and output now</Link>
        </Button>
      </main>
      <Footer />
    </>
  );
}
