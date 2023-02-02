import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { UserTable } from "src/components/UserTable";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

/**
 * Provides the admin index page that will display a list of users and give
 * admins the ability to manage their access rights.
 */
const AdminIndex = () => {
  return (
    <AdminArea title="Open Assistant">
      <UserTable />
    </AdminArea>
  );
};

AdminIndex.getLayout = getAdminLayout;

export default AdminIndex;
