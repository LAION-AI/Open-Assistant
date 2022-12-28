import Head from "next/head";
import { useSession } from "next-auth/react";

import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Hero } from "src/components/Hero";
import { TaskSelection } from "src/components/TaskSelection";

const Home = () => {
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
      {session ? (
        <main className="my-4">
          <TaskSelection />
        </main>
      ) : (
        <main>
          <Hero />
          <CallToAction />

          <Faq />
        </main>
      )}
    </>
  );
};

export default Home;
