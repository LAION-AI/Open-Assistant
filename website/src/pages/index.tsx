import { useSession } from "next-auth/react";
import Head from "next/head";
import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Footer } from "src/components/Footer";
import { Header } from "src/components/Header";
import { Hero } from "src/components/Hero";
import { TaskSelection } from "src/components/TaskSelection";

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
      <main className="m-20 z-0 bg-white flex flex-col items-center justify-center gap-2">
        <TaskSelection />
      </main>
      <Footer />
    </>
  );
}
