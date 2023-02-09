import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  CircularProgress,
  Container,
  FormControl,
  FormLabel,
  Input,
  Stack,
  useToast,
} from "@chakra-ui/react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useForm } from "react-hook-form";
import { AdminArea } from "src/components/AdminArea";
import { JsonCard } from "src/components/JsonCard";
import { getAdminLayout } from "src/components/Layout";
import { AdminMessageTable } from "src/components/Messages/AdminMessageTable";
import { Role, RoleSelect } from "src/components/RoleSelect";
import { get, post } from "src/lib/api";
import { userlessApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { Message } from "src/types/Conversation";
import { User } from "src/types/Users";
import useSWRImmutable from "swr/immutable";
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
      <AdminArea>
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
                  <FormControl mt="2">
                    <FormLabel>Role</FormLabel>
                    <RoleSelect {...register("role")}></RoleSelect>
                  </FormControl>
                  <FormControl mt="2">
                    <FormLabel>Notes</FormLabel>
                    <Input {...register("notes")} />
                  </FormControl>
                  <FormControl mt="2">
                    <FormLabel>Show on leaderboard</FormLabel>
                    <Checkbox></Checkbox>
                  </FormControl>
                  <Button mt={4} type="submit">
                    Update
                  </Button>
                </form>
                <Accordion allowToggle mt="4">
                  <AccordionItem>
                    <AccordionButton>
                      <Box as="span" flex="1" textAlign="left">
                        Raw JSON
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                    <AccordionPanel pb={4}>
                      <JsonCard>{user}</JsonCard>
                    </AccordionPanel>
                  </AccordionItem>
                </Accordion>
              </CardBody>
            </Card>
          </Container>
          <Card>
            <CardHeader fontWeight="medium" fontSize="xl">
              Messages
            </CardHeader>
            <CardBody>
              <UserMessageTable id={user.user_id}></UserMessageTable>
            </CardBody>
          </Card>
        </Stack>
      </AdminArea>
    </>
  );
};

const UserMessageTable = ({ id }: { id: User["id"] }) => {
  const { data, error, isLoading } = useSWRImmutable<Message[] | null>(`/api/admin/user_messages?user=${id}`, get);

  if (isLoading) {
    return <CircularProgress isIndeterminate />;
  }

  if (error) {
    return <>Unable to load messages.</>;
  }

  console.log(data);

  return <AdminMessageTable messages={data || []}></AdminMessageTable>;
};

/**
 * Fetch the user's data on the server side when rendering.
 */
export const getServerSideProps: GetServerSideProps<{ user: User<Role> }, { id: string }> = async ({
  params,
  locale = "en",
}) => {
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const backend_user = await userlessApiClient.fetch_user(params!.id as string);

  if (!backend_user) {
    return {
      notFound: true,
    };
  }
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
};

ManageUser.getLayout = getAdminLayout;

export default ManageUser;
