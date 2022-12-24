import Head from "next/head";
import { getCsrfToken, getProviders, signIn } from "next-auth/react";
import Link from "next/link";

import { AuthLayout } from "src/components/AuthLayout";

export default function Verify() {
  return (
    <>
      <Head>
        <title>Sign Up - Open Assistant</title>
        <meta name="Sign Up" content="Sign up to access Open Assistant" />
      </Head>
      <AuthLayout>
        <h1 className="text-lg">A sign-in link has been sent to your email address.</h1>
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
