// https://nextjs.org/docs/basic-features/layouts

import { Box, Grid } from "@chakra-ui/react";
import { Activity, BarChart2, HelpCircle, Layout, MessageSquare, Settings, Users } from "lucide-react";
import type { NextPage } from "next";
import { Header } from "src/components/Header";

import { SlimFooter } from "./Dashboard/SlimFooter";
import { Footer } from "./Footer";
import { SideMenuLayout } from "./SideMenuLayout";

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
    <SideMenuLayout
      menuButtonOptions={[
        {
          label: "Dashboard",
          pathname: "/dashboard",
          icon: Layout,
        },
        {
          label: "Messages",
          pathname: "/messages",
          icon: MessageSquare,
        },
        {
          label: "Leaderboard",
          pathname: "/leaderboard",
          icon: BarChart2,
        },
        {
          label: "Guidelines",
          pathname: "https://projects.laion.ai/Open-Assistant/docs/guides/guidelines",
          icon: HelpCircle,
          target: "_blank",
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
  </Grid>
);

export const getAdminLayout = (page: React.ReactElement) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header />
    <SideMenuLayout
      menuButtonOptions={[
        {
          label: "Users",
          pathname: "/admin",
          icon: Users,
        },
        {
          label: "Status",
          pathname: "/admin/status",
          icon: Activity,
        },
        {
          label: "Parameters",
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
