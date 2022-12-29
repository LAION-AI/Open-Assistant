import Head from "next/head";
import { useSession } from "next-auth/react";

import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Hero } from "src/components/Hero";
import { TaskSelection } from "src/components/TaskSelection";
import { Header } from "src/components/Header";
import { Footer } from "src/components/Footer";
import { Box, Container } from "@chakra-ui/react";

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
        <Container>
          <TaskSelection />
        </Container>
      ) : (
        <Container className="min-w-full">
          <Hero />
          <CallToAction />
          <Faq />
        </Container>
      )}
    </>
  );
};

Home.getLayout = (page) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header transparent={true} />
    {page}
    <Footer />
  </div>
);

export default Home;
