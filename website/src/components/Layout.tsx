// https://nextjs.org/docs/basic-features/layouts

import { Box, Grid } from "@chakra-ui/react";
import { Activity, BarChart2, Layout, MessageSquare, Settings, Users } from "lucide-react";
import type { NextPage } from "next";
import { Header } from "src/components/Header";

import { SlimFooter } from "./Dashboard/SlimFooter";
import { Footer } from "./Footer";
import { SideMenuLayout } from "./SideMenuLayout";
import { ToSWrapper } from "./ToSWrapper";

export type NextPageWithLayout<P = unknown, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: React.ReactElement) => React.ReactNode;
};

export const getDefaultLayout = (page: React.ReactElement) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header />
    {page}
    <Footer />
  </div>
);

export const getTransparentHeaderLayout = (page: React.ReactElement) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header />
    {page}
    <Footer />
  </div>
);

export const getDashboardLayout = (page: React.ReactElement) => (
  <Grid templateRows="min-content 1fr" h="full">
    <Header />
    <ToSWrapper>
      <SideMenuLayout
        menuButtonOptions={[
          {
            labelID: "dashboard",
            pathname: "/dashboard",
            icon: Layout,
          },
          {
            labelID: "messages",
            pathname: "/messages",
            icon: MessageSquare,
          },
          {
            labelID: "leaderboard",
            pathname: "/leaderboard",
            icon: BarChart2,
          },
        ]}
      >
        <Grid templateRows="1fr min-content" h="full">
          <Box>{page}</Box>
          <Box mt="10">
            <SlimFooter />
          </Box>
        </Grid>
      </SideMenuLayout>
    </ToSWrapper>
  </Grid>
);

export const getAdminLayout = (page: React.ReactElement) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header />
    <SideMenuLayout
      menuButtonOptions={[
        {
          labelID: "users",
          pathname: "/admin",
          icon: Users,
        },
        {
          labelID: "status",
          pathname: "/admin/status",
          icon: Activity,
        },
        {
          labelID: "parameters",
          pathname: "/admin/parameters",
          icon: Settings,
        },
      ]}
    >
      {page}
    </SideMenuLayout>
  </div>
);

export const noLayout = (page: React.ReactElement) => page;
