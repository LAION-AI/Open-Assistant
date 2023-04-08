import { Card, CardBody } from "@chakra-ui/react";
import Head from "next/head";
import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { AdminMessageTable } from "src/components/Messages/AdminMessageTable";
export { getServerSideProps } from "src/lib/defaultServerSideProps";

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
