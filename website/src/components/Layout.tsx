// https://nextjs.org/docs/basic-features/layouts

import { Box, Grid } from "@chakra-ui/react";
import { Activity, BarChart2, Layout, MessageSquare, Users } from "lucide-react";
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
          desc: "Dashboard Home",
          icon: Layout,
        },
        {
          label: "Messages",
          pathname: "/messages",
          desc: "Messages Dashboard",
          icon: MessageSquare,
        },
        {
          label: "Leaderboard",
          pathname: "/leaderboard",
          desc: "User Leaderboard",
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
          desc: "Users Dashboard",
          icon: Users,
        },
        {
          label: "Status",
          pathname: "/admin/status",
          desc: "Status Dashboard",
          icon: Activity,
        },
      ]}
    >
      {page}
    </SideMenuLayout>
  </div>
);

export const noLayout = (page: React.ReactElement) => page;
