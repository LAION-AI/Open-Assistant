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
  FormControl,
  FormLabel,
  Input,
  Stack,
  Flex,
  useToast,
  Grid,
  Text,
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
import { post } from "src/lib/api";
import { getValidDisplayName } from "src/lib/display_name_validation";
import { userlessApiClient } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { getFrontendUserIdForDiscordUser } from "src/lib/users";
import { User } from "src/types/Users";
import useSWRMutation from "swr/mutation";
import uswSWRImmutable from "swr/immutable";
import { useTranslation } from "next-i18next";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { get } from "src/lib/api";

interface UserForm {
  user_id: string;
  id: string;
  auth_method: string;
  display_name: string;
  role: Role;
  notes: string;
  show_on_leaderboard: boolean;
}

const ManageUser = ({ user }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation("leaderboard");
  const toast = useToast();

  const { data: entries } = uswSWRImmutable<Partial<{ [time in LeaderboardTimeFrame]: LeaderboardEntity }>>(
    "/api/user_stats?uid=" + user.id,
    get,
    {
      fallbackData: {},
    }
  );

  // Trigger to let us update the user's role.  Triggers a toast when complete.
  const { trigger } = useSWRMutation("/api/admin/update_user", post, {
    onSuccess: () => {
      toast({
        title: "Updated user",
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
                  <Checkbox {...register("show_on_leaderboard")}></Checkbox>
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
          <Card>
            <CardHeader pb="0" fontWeight="medium" fontSize="xl">
              {`User's messages`}
            </CardHeader>
            <CardBody>
              <AdminMessageTable userId={user.user_id}></AdminMessageTable>
            </CardBody>
          </Card>

          <SurveyCard>
            <Title>{t("user_stats")}</Title>
            {[
              LeaderboardTimeFrame.day,
              LeaderboardTimeFrame.week,
              LeaderboardTimeFrame.month,
              LeaderboardTimeFrame.total,
            ]
              .map((key) => ({ key, values: entries[key] }))
              .filter(({ values }) => values)
              .map(({ key, values }) => (
                <Box key={key} py={4}>
                  <Title>{t(getTypeSafei18nKey(key))}</Title>
                  <Flex w="full" wrap="wrap" alignItems="flex-start" gap={4}>
                    <TableColumn>
                      <Entry title={t("score")} value={values.leader_score} />
                      <Entry title={t("rank")} value={values.rank} />
                      <Entry title={t("prompt")} value={values.prompts} />
                      <Entry title={t("accepted_prompts")} value={values.accepted_prompts} />
                    </TableColumn>
                    <TableColumn>
                      <Entry title={t("replies_assistant")} value={values.replies_assistant} />
                      <Entry title={t("accepted")} value={values.accepted_replies_assistant} />
                      <Entry title={t("replies_prompter")} value={values.replies_prompter} />
                      <Entry title={t("accepted")} value={values.accepted_replies_prompter} />
                    </TableColumn>
                    <TableColumn>
                      <Entry title={t("labels_full")} value={values.labels_full} />
                      <Entry title={t("labels_simple")} value={values.labels_simple} />
                      <Entry title={t("rankings")} value={values.rankings_total} />
                      <Entry title={t("reply_ranked_1")} value={values.reply_ranked_1} />
                    </TableColumn>
                  </Flex>
                </Box>
              ))}
          </SurveyCard>
        </Stack>
      </AdminArea>
    </>
  );
};

const TableColumn = ({ children }) => {
  return (
    <Grid gridTemplateColumns="1fr max-content" mx={8} w="60" gap={2}>
      {children}
    </Grid>
  );
};

const Entry = ({ title, value }) => {
  return (
    <>
      <span className="text-start">{title}</span>
      <span className="text-end">{value}</span>
    </>
  );
};

const Title = ({ children }) => (
  <Text as="b" display="block" fontSize="2xl" py={2}>
    {children}
  </Text>
);

/**
 * Fetch the user's data on the server side when rendering.
 */
export const getServerSideProps: GetServerSideProps<{ user: User<Role> }, { id: string }> = async ({
  params,
  locale = "en",
}) => {
  const backend_user = await userlessApiClient.fetch_user(params!.id as string);
  if (!backend_user) {
    return {
      notFound: true,
    };
  }

  let frontendUserId = backend_user.id;
  if (backend_user.auth_method === "discord") {
    frontendUserId = await getFrontendUserIdForDiscordUser(backend_user.id);
  }

  const local_user = await prisma.user.findUnique({
    where: { id: frontendUserId },
    select: { role: true },
  });

  if (!local_user) {
    return {
      notFound: true,
    };
  }

  const user = {
    ...backend_user,
    role: (local_user?.role || "general") as Role,
  };
  user.display_name = getValidDisplayName(user.display_name, user.id);
  return {
    props: {
      user,
      ...(await serverSideTranslations(locale, ["common", "message"])),
    },
  };
};

ManageUser.getLayout = getAdminLayout;

export default ManageUser;
