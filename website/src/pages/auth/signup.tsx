import { Box, Button, ButtonGroup, Input, Stack } from "@chakra-ui/react";
import Head from "next/head";
import { FaDiscord, FaEnvelope, FaGithub, FaMagic } from "react-icons/fa";
import { getCsrfToken, getProviders, signIn } from "next-auth/react";
import { useRef } from "react";
import Link from "next/link";

import { AuthLayout } from "src/components/AuthLayout";

export default function Signin({ csrfToken, providers }) {
  const { discord, email } = providers;
  const emailEl = useRef(null);
  const signinWithEmail = () => {
    signIn(email.id, { callbackUrl: "/", email: emailEl.current.value });
  };

  return (
    <>
      <Head>
        <title>Sign Up - Open Assistant</title>
        <meta name="Sign Up" content="Sign up to access Open Assistant" />
      </Head>
      <AuthLayout>
        <Stack spacing="2">
          {email && (
            <Stack>
              <Input variant="outline" size="lg" placeholder="Email Address" ref={emailEl} />
              <Button
                size={"lg"}
                leftIcon={<FaEnvelope />}
                colorScheme="gray"
                onClick={signinWithEmail}
                // isDisabled="false"
              >
                Continue with Email
              </Button>
            </Stack>
          )}
          {/* {discord && ( */}
          <Button
            bg="#5865F2"
            _hover={{ bg: "#4A57E3" }}
            _active={{
              bg: "#454FBF",
            }}
            // Uses official Discord 'Blurple' colors
            size="lg"
            // isDisabled="true"
            leftIcon={<FaDiscord />}
            color="white"
            // onClick={() => signIn(discord.id, { callbackUrl: "/" })}
          >
            Continue with Discord
          </Button>
          {/* )} */}
          <Button
            bg="#333333"
            _hover={{ bg: "#181818" }}
            _active={{
              bg: "#101010",
            }}
            size={"lg"}
            // isDisabled="true"
            leftIcon={<FaGithub />}
            colorScheme="blue"
          >
            Continue with Github
          </Button>
        </Stack>
        <hr className="mt-14 mb-4 h-px bg-gray-200 border-0" />
        <Link
          href="#"
          aria-label="Log In"
          className="flex justify-center font-medium text-black hover:underline underline-offset-4"
        >
          Already have an account? Log In
        </Link>
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
