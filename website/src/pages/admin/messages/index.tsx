import { CircularProgress } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { get } from "src/lib/api";
import { FetchUserMessagesCursorResponse } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

const MessageList = () => {
  const router = useRouter();
  const { data, isLoading, error } = useSWRImmutable<FetchUserMessagesCursorResponse>(`/api/admin/messages/`, get);
  console.log(data);
  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <AdminArea>
        {isLoading && <CircularProgress isIndeterminate></CircularProgress>}
        {error && "Unable to load message tree"}
      </AdminArea>
    </>
  );
};

MessageList.getLayout = getAdminLayout;

export default MessageList;

export const getServerSideProps: GetServerSideProps = async ({ locale = "en" }) => {
  return {
    props: {
      ...(await serverSideTranslations(locale, ["common", "labelling", "message"])),
    },
  };
};
