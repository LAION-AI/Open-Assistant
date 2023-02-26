import React from "react";
import {
  Box,
  Card,
  CardBody,
  Heading,
  Radio,
  RadioGroup,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useBoolean,
} from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { AdminArea } from "src/components/AdminArea";
import { getAdminLayout } from "src/components/Layout";
import { TrollboardTable } from "src/components/LeaderboardTable/TrollboardTable";
import { TrollboardTimeFrame } from "src/types/Trollboard";

const Leaderboard = () => {
  const { t } = useTranslation(["leaderboard", "common"]);
  const [enabled, setEnabled] = useBoolean(true);

  return (
    <>
      <Head>
        <title>{`Trollboard - ${t("common:title")}`}</title>
        <meta name="description" content="Admin Trollboard" charSet="UTF-8" />
      </Head>
      <AdminArea>
        <Box display="flex" flexDirection="column">
          <Heading fontSize="2xl" fontWeight="bold" pb="4">
            Trollboard
          </Heading>
          <Card>
            <CardBody>
              <RadioGroup defaultValue="1" onChange={setEnabled.toggle}>
                <Stack direction="row" spacing={5}>
                  <Radio value="1" colorScheme="green">
                    Show active users
                  </Radio>
                  <Radio value="2" colorScheme="red">
                    Show banned users
                  </Radio>
                </Stack>
              </RadioGroup>
              <Tabs isFitted isLazy>
                <TabList mb={4}>
                  <Tab>{t("daily")}</Tab>
                  <Tab>{t("weekly")}</Tab>
                  <Tab>{t("monthly")}</Tab>
                  <Tab>{t("overall")}</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel p="0">
                    <TrollboardTable
                      timeFrame={TrollboardTimeFrame.day}
                      limit={100}
                      rowPerPage={20}
                      enabled={enabled}
                    />
                  </TabPanel>
                  <TabPanel p="0">
                    <TrollboardTable
                      timeFrame={TrollboardTimeFrame.week}
                      limit={100}
                      rowPerPage={20}
                      enabled={enabled}
                    />
                  </TabPanel>
                  <TabPanel p="0">
                    <TrollboardTable
                      timeFrame={TrollboardTimeFrame.month}
                      limit={100}
                      rowPerPage={20}
                      enabled={enabled}
                    />
                  </TabPanel>
                  <TabPanel p="0">
                    <TrollboardTable
                      timeFrame={TrollboardTimeFrame.total}
                      limit={100}
                      rowPerPage={20}
                      enabled={enabled}
                    />
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>
        </Box>
      </AdminArea>
    </>
  );
};

Leaderboard.getLayout = getAdminLayout;

export default Leaderboard;
