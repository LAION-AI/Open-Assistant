import { Button, Input, Stack } from "@chakra-ui/react";
import Head from "next/head";
import { FaDiscord, FaEnvelope, FaGithub } from "react-icons/fa";
import { getCsrfToken, getProviders, signIn } from "next-auth/react";
import { useRef } from "react";
import Link from "next/link";

import { AuthLayout } from "src/components/AuthLayout";

export default function Signin({ csrfToken, providers }) {
  const { discord, email, github } = providers;
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
              onClick={() => signIn(discord, { callbackUrl: "/" })}
              // isDisabled="false"
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
              // isDisabled="false"
            >
              Continue with Github
            </Button>
          )}
        </Stack>
        <div className="pt-10 text-center">
          By signing up you agree to our <br></br>
          <Link href="#" aria-label="Terms of Service" className="hover:underline underline-offset-4">
            <b>Terms of Service</b>
          </Link>{" "}
          and{" "}
          <Link href="#" aria-label="Terms of Use" className="hover:underline underline-offset-4">
            <b>Privacy Policy</b>
          </Link>
          .
        </div>
        <hr className="mt-14 mb-4 h-px bg-gray-200 border-0" />
        <div className="text-center">
          Already have an account?{" "}
          <Link href="#" aria-label="Log In" className="hover:underline underline-offset-4">
            <b>Log In</b>
          </Link>
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
