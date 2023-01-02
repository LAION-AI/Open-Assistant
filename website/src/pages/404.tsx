import Head from "next/head";

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
