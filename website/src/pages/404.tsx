import { useSession } from "next-auth/react";
import { Footer } from "../components/Footer";
import { Header } from "@/components/Header/Header";
import Head from "next/head";
import Link from "next/link";

export default function Error() {
  const { data: session } = useSession();

  if (!session) {
    return (
      <>
        <Head>
          <title>Open Assistant</title>
          <meta name="404" content="Sorry, this page doesn't exist." />
        </Head>
        <Header />
        <main className="flex h-3/4 items-center justify-center overflow-hidden subpixel-antialiased text-xl">
          {"Sorry, the page you're looking for does not exist."}
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
      <main>
        <h2>Open Chat Gpt</h2>

        <p>You are logged in</p>

        <Link href="/grading/grade-output">~Rate a prompt and output now~</Link>
      </main>
      <Footer />
    </>
  );
}
