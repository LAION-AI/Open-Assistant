import { Button, Container, FormControl, FormLabel, Input, Select, useToast } from "@chakra-ui/react";
import { Field, Form, Formik } from "formik";
import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useEffect } from "react";
import { getAdminLayout } from "src/components/Layout";
import poster from "src/lib/poster";
import prisma from "src/lib/prismadb";
import useSWRMutation from "swr/mutation";

const ManageUser = ({ user }) => {
  const toast = useToast();
  const router = useRouter();
  const { data: session, status } = useSession();

  // Check when the user session is loaded and re-route if the user is not an
  // admin.  This follows the suggestion by NextJS for handling private pages:
  //   https://nextjs.org/docs/api-reference/next/router#usage
  //
  // All admin pages should use the same check and routing steps.
  useEffect(() => {
    if (status === "loading") {
      return;
    }
    if (session?.user?.role === "admin") {
      return;
    }
    router.push("/");
  }, [router, session, status]);

  // Trigger to let us update the user's role.  Triggers a toast when complete.
  const { trigger } = useSWRMutation("/api/admin/update_user", poster, {
    onSuccess: () => {
      toast({
        title: "User Role Updated",
        status: "success",
        duration: 1000,
        isClosable: true,
      });
    },
    onError: () => {
      toast({
        title: "User Role update failed",
        status: "error",
        duration: 1000,
        isClosable: true,
      });
    },
  });

  return (
    <>
      <Head>
        <title>Manage Users - Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <Container className="oa-basic-theme">
        <Formik
          initialValues={user}
          onSubmit={(values) => {
            trigger(values);
          }}
        >
          <Form>
            <Field name="id" type="hidden" />
            <Field name="name">
              {({ field }) => (
                <FormControl>
                  <FormLabel>Username</FormLabel>
                  <Input {...field} isDisabled />
                </FormControl>
              )}
            </Field>
            <Field name="email">
              {({ field }) => (
                <FormControl>
                  <FormLabel>Email</FormLabel>
                  <Input {...field} isDisabled />
                </FormControl>
              )}
            </Field>

            <Field name="role">
              {({ field }) => (
                <FormControl>
                  <FormLabel>Role</FormLabel>
                  <Select {...field}>
                    <option value="banned">Banned</option>
                    <option value="general">General</option>
                    <option value="admin">Admin</option>
                  </Select>
                </FormControl>
              )}
            </Field>
            <Button mt={4} type="submit">
              Update
            </Button>
          </Form>
        </Formik>
      </Container>
    </>
  );
};

/**
 * Fetch the user's data on the server side when rendering.
 */
export async function getServerSideProps({ query }) {
  const user = await prisma.user.findUnique({
    where: { id: query.id },
    select: {
      id: true,
      name: true,
      email: true,
      role: true,
    },
  });
  return {
    props: {
      user,
    },
  };
}

ManageUser.getLayout = getAdminLayout;

export default ManageUser;
