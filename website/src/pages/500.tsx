import { Button, Link, Stack } from "@chakra-ui/react";
import Head from "next/head";
import NextLink from "next/link";
import { FiAlertTriangle } from "react-icons/fi";

export default function Error() {
  return (
    <>
      <Head>
        <title>500 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <main className="flex h-3/4 items-center justify-center overflow-hidden subpixel-antialiased text-xl">
        <Stack>
          <p>Sorry, We encountered a server error. We&apos;re not sure what went wrong</p>
          <p>Please file a but below and describe what you were trying to accomplish</p>
          <Button leftIcon={<FiAlertTriangle className="text-blue-500" aria-hidden="true" />} variant="solid">
            <Link
              as={NextLink}
              key="Report a Bug"
              href="https://github.com/LAION-AI/Open-Assistant/issues/new/choose"
              aria-label="Report a Bug"
              className="flex items-center"
            >
              Report a Bug
            </Link>
          </Button>
        </Stack>
      </main>
    </>
  );
}
