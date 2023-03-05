// https://nextjs.org/docs/basic-features/layouts

import { Box, Grid } from "@chakra-ui/react";
import { Activity, BarChart2, ExternalLink, Layout, MessageSquare, Settings, TrendingUp, Users } from "lucide-react";
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
  <Grid templateRows="min-content 1fr" h="full" gridTemplateColumns="minmax(0, 1fr)">
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
          {
            labelID: "stats",
            pathname: "/stats",
            icon: TrendingUp,
          },
          {
            labelID: "guidelines",
            pathname: "https://projects.laion.ai/Open-Assistant/docs/guides/guidelines",
            icon: ExternalLink,
            target: "_blank",
          },
        ]}
      >
        <Box>{page}</Box>
        <Box mt="10">
          <SlimFooter />
        </Box>
      </SideMenuLayout>
    </ToSWrapper>
  </Grid>
);

export const getAdminLayout = (page: React.ReactElement) => (
  <Grid templateRows="min-content 1fr" h="full" gridTemplateColumns="minmax(0, 1fr)">
    <Header />
    <SideMenuLayout
      menuButtonOptions={[
        {
          labelID: "users",
          pathname: "/admin",
          icon: Users,
        },
        {
          labelID: "trollboard",
          pathname: "/admin/trollboard",
          icon: BarChart2,
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
  </Grid>
);

export const noLayout = (page: React.ReactElement) => page;
