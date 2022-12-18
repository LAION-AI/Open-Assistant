import { Auth, ThemeSupa } from "@supabase/auth-ui-react";
import { useSession, useSupabaseClient } from "@supabase/auth-helpers-react";

import Head from "next/head";

import { CallToAction } from "../components/CallToAction";
import { Faq } from "../components/Faq";
import { Footer } from "../components/Footer";
import { Header } from "../components/Header";
import { Hero } from "../components/Hero";

import styles from "../styles/Home.module.css";

export default function Home() {
  const session = useSession();
  const supabase = useSupabaseClient();

  const signinWithDiscord = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "discord",
    });
  };

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
        <main>
          <Hero />
          <CallToAction />

          <Faq />
        </main>
        <Footer />
      </>
    );
  }
  return (
    <div className={styles.App}>
      <header className={styles.AppHeader}>
        {/* <img src={logo} className="App-logo" alt="logo" /> */}

        <h2>Open Chat Gpt</h2>

        <p>You are logged in</p>
      </header>
    </div>
  );
}
