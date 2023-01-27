import { Button, Card, CardBody, Container, FormControl, FormLabel, Input, Stack, useToast } from "@chakra-ui/react";
import { InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { getAdminLayout } from "src/components/Layout";
import { Role, RoleSelect } from "src/components/RoleSelect";
import { UserMessagesCell } from "src/components/UserMessagesCell";
import { post } from "src/lib/api";
import { userlessApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import useSWRMutation from "swr/mutation";

interface UserForm {
  user_id: string;
  id: string;
  auth_method: string;
  display_name: string;
  role: Role;
  notes: string;
}

const ManageUser = ({ user }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
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
  const { trigger } = useSWRMutation("/api/admin/update_user", post, {
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

  const { register, handleSubmit } = useForm<UserForm>({
    defaultValues: user,
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
      <Stack gap="4">
        <Container>
          <Card>
            <CardBody>
              <form onSubmit={handleSubmit((data) => trigger(data))}>
                <input type="hidden" {...register("user_id")}></input>
                <input type="hidden" {...register("id")}></input>
                <input type="hidden" {...register("auth_method")}></input>
                <FormControl>
                  <FormLabel>Display Name</FormLabel>
                  <Input {...register("display_name")} isDisabled />
                </FormControl>
                <FormControl>
                  <FormLabel>Role</FormLabel>
                  <RoleSelect {...register("role")}></RoleSelect>
                </FormControl>
                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Input {...register("notes")} />
                </FormControl>
                <Button mt={4} type="submit">
                  Update
                </Button>
              </form>
            </CardBody>
          </Card>
        </Container>
        <UserMessagesCell path={`/api/admin/user_messages?user=${user.user_id}`} />
      </Stack>
    </>
  );
};

/**
 * Fetch the user's data on the server side when rendering.
 */
export async function getServerSideProps({ query, locale }) {
  const backend_user = await userlessApiClient.fetch_user(query.id);
  const local_user = await prisma.user.findUnique({
    where: { id: backend_user.id },
    select: {
      role: true,
    },
  });
  const user = {
    ...backend_user,
    role: (local_user?.role || "general") as Role,
  };
  return {
    props: {
      user,
      ...(await serverSideTranslations(locale, ["common"])),
    },
  };
}

ManageUser.getLayout = getAdminLayout;

export default ManageUser;
