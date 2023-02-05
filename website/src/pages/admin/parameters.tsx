import { Card, CardBody, CircularProgress } from "@chakra-ui/react";
import Head from "next/head";
import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { get } from "src/lib/api";
import useSWRImmutable from "swr/immutable";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

export default function Parameters() {
  const { data, isLoading, error } = useSWRImmutable("/api/admin/parameters", get);

  return (
    <>
      <Head>
        <title>Parameters - Open Assistant</title>
      </Head>
      <AdminArea>
        <Card>
          <CardBody>
            {isLoading && <CircularProgress isIndeterminate></CircularProgress>}
            {error && "Unable to load data"}
            {data && (
              <Card variant="json" overflowX="auto">
                <CardBody>
                  <pre>{JSON.stringify(data, null, 2)}</pre>
                </CardBody>
              </Card>
            )}
          </CardBody>
        </Card>
      </AdminArea>
    </>
  );
}

Parameters.getLayout = getAdminLayout;
