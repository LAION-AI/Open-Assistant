import axios from "axios";
import Head from "next/head";
import Image from "next/image";
import { useSession, signIn, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import useSWR from "swr";

import styles from "../styles/Home.module.css";

const fetcher = (url) => axios.get(url).then((res) => res.data);

export default function Home() {
  const { data: session, status } = useSession();
  const { data: prompts, errors } = useSWR(
    session ? "/api/prompts" : null,
    fetcher
  );
  if (!session) {
    return (
      <div className={styles.App}>
        <header className={styles.AppHeader}>
          {/* <img src={logo} className="App-logo" alt="logo" /> */}
          <h2>Open Chat Gpt</h2>
          <p>
            Open chat gpt is a project meant to give everyone access to a great
            chat based large language model.
          </p>

          <button onClick={signIn}>Register</button>
          <p>
            We believe that by doing this we will create a revolution in
            innovation in language. In the same way that stable-diffusion helped
            the world make art and images in new ways we hope open chat gpt can
            help improve the world by improving language itself.
          </p>

          <h2>How can you help?</h2>
          <p>
            All open source projects begins with people like you. Open source is
            the belief that if we collaborate we can together gift our knowledge
            and technology to the world for the benefit of humanity.
          </p>

          <h2>I am in! Now what?</h2>
          <p>We live and collaborate the work in the LAION discord. Join us!</p>
          <a
            className={styles.AppLink}
            href="https://discord.gg/RQFtmAmk"
            target="_blank"
            rel="noopener noreferrer"
          >
            Join us on Discord
          </a>
        </header>
      </div>
    );
  }

  console.log(prompts);
  return (
    <div className={styles.App}>
      <header className={styles.AppHeader}>
        {/* <img src={logo} className="App-logo" alt="logo" /> */}

        <h2>Open Chat Gpt</h2>

        <p>You are logged in</p>

        <button onClick={signOut}>Signout</button>
      </header>
    </div>
  );
}
