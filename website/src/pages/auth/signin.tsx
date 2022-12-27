import { Button, Input, Stack } from "@chakra-ui/react";
import Head from "next/head";
import Link from "next/link";
import { useRef } from "react";
import { FaDiscord, FaEnvelope, FaGithub } from "react-icons/fa";
import { getCsrfToken, getProviders, signIn } from "next-auth/react";

import { AuthLayout } from "src/components/AuthLayout";

export default function Signin({ csrfToken, providers }) {
  const { discord, email, github } = providers;
  const emailEl = useRef(null);
  const signinWithEmail = () => {
    signIn(email.id, { callbackUrl: "/", email: emailEl.current.value });
  };
  const signinWithDiscord = () => {
    signIn(discord.id, { callbackUrl: "/" });
  };
  const signinWithGithub = () => {
    signIn(github.id, { callbackUrl: "/" });
  };

  return (
    <>
      <Head>
        <title>Sign In - Open Assistant</title>
        <meta name="Sign In" content="Sign in to access Open Assistant" />
      </Head>
      <AuthLayout>
        <Stack spacing="2">
          {email && (
            <Stack className="mb-4">
              <Input variant="outline" size="lg" placeholder="Email Address" ref={emailEl} />
              <Button size={"lg"} leftIcon={<FaEnvelope />} colorScheme="gray" onClick={signinWithEmail}>
                Continue with Email
              </Button>
            </Stack>
          )}
          {discord && (
            <Button
              bg="#5865F2"
              _hover={{ bg: "#4A57E3" }}
              _active={{
                bg: "#454FBF",
              }}
              size="lg"
              leftIcon={<FaDiscord />}
              color="white"
              onClick={signinWithDiscord}
            >
              Continue with Discord
            </Button>
          )}
          {github && (
            <Button
              bg="#333333"
              _hover={{ bg: "#181818" }}
              _active={{
                bg: "#101010",
              }}
              size={"lg"}
              leftIcon={<FaGithub />}
              colorScheme="blue"
              onClick={signinWithGithub}
            >
              Continue with Github
            </Button>
          )}
        </Stack>
        <hr className="mt-14 mb-4 h-px bg-gray-200 border-0" />
        <div className="text-center">
          By continuing you agree to our <br></br>
          <Link href="#" aria-label="Terms of Service" className="hover:underline underline-offset-4">
            <b>Terms of Service</b>
          </Link>{" "}
          and{" "}
          <Link href="#" aria-label="Terms of Use" className="hover:underline underline-offset-4">
            <b>Privacy Policy</b>
          </Link>
          .
        </div>
      </AuthLayout>
    </>
  );
}

export async function getServerSideProps(context) {
  const csrfToken = await getCsrfToken();
  const providers = await getProviders();
  return {
    props: {
      csrfToken,
      providers,
    },
  };
}
