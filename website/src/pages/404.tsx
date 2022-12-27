import { useSession } from "next-auth/react";
import { Footer } from "../components/Footer";
import { Header } from "../components/Header";
import Head from "next/head";
import Link from "next/link";

export default function Error() {
  return (
    <>
      <Head>
        <title>404 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Header />
      <main className="flex h-3/4 items-center justify-center overflow-hidden subpixel-antialiased text-xl">
        Sorry, the page you're looking for does not exist.
      </main>
      <Footer />
    </>
  );
}
