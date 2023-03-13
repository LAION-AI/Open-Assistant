import { Card, CardBody } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { AdminMessageTable } from "src/components/Messages/AdminMessageTable";

const MessageList = () => {
  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <AdminArea>
        <Card>
          <CardBody>
            <AdminMessageTable includeUser></AdminMessageTable>
          </CardBody>
        </Card>
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
