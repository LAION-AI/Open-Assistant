import { useSession } from "next-auth/react";
import { Footer } from "../components/Footer";
import { Header } from "src/components/Header";
import Head from "next/head";
import Link from "next/link";

export default function Error() {
  return (
    <>
      <Head>
        <title>404 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <main className="flex h-3/4 items-center justify-center overflow-hidden subpixel-antialiased text-xl">
        <p>Sorry, the page you are looking for does not exist.</p>
      </main>
    </>
  );
}
