import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useEffect } from "react";
import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Hero } from "src/components/Hero";
import { getTransparentHeaderLayout } from "src/components/Layout";

const Home = () => {
  const router = useRouter();
  const { status } = useSession();
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [router, status]);

  return (
    <>
      <Head>
        <title>Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <main className="oa-basic-theme">
        <Hero />
        <CallToAction />
        <Faq />
      </main>
    </>
  );
};

Home.getLayout = getTransparentHeaderLayout;

export default Home;
