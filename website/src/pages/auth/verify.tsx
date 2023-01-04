import Head from "next/head";
import { getCsrfToken, getProviders } from "next-auth/react";
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
      </AuthLayout>
    </>
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
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
