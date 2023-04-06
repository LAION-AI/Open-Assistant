import Head from "next/head";
import { AdminArea } from "src/components/AdminArea";
import { AdminLayout } from "src/components/Layout";
import { UserTable } from "src/components/UserTable";
export { getStaticProps } from "src/lib/defaultServerSideProps";

/**
 * Provides the admin index page that will display a list of users and give
 * admins the ability to manage their access rights.
 */
const AdminIndex = () => {
  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <AdminArea>
        <UserTable />
      </AdminArea>
    </>
  );
};

AdminIndex.getLayout = AdminLayout;

export default AdminIndex;
