import { Button, Input } from "@chakra-ui/react";
import Head from "next/head";
import { FaDiscord, FaGithub, FaMagic } from "react-icons/fa";
import { getCsrfToken, getProviders, signIn } from "next-auth/react";
import { useRef } from "react";

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
        <title>Log in</title>
      </Head>
      <AuthLayout title="Log In" subtitle={<></>}>
        <div className="space-y-6 w-100 flex flex-col justify-center items-center ">
          {discord && (
            <Button
              leftIcon={<FaDiscord />}
              colorScheme="blue"
              size="lg"
              w="36"
              onClick={() => signIn(discord.id, { callbackUrl: "/" })}
            >
              Discord
            </Button>
          )}

          <Button w="36" leftIcon={<FaGithub />} colorScheme="blue" size="lg">
            Github
          </Button>

          {email && (
            <div>
              <Input variant="outline" placeholder="Email Address" ref={emailEl} />
              <Button w="36" leftIcon={<FaMagic />} colorScheme="blue" size="lg" onClick={signinWithEmail}>
                Email
              </Button>
            </div>
          )}
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
