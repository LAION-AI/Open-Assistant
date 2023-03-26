// https://nextjs.org/docs/basic-features/layouts

import { Box } from "@chakra-ui/react";
import { Activity, BarChart2, ExternalLink, Layout, MessageSquare, Settings, TrendingUp, Users } from "lucide-react";
import type { NextPage } from "next";

import { SlimFooter } from "./Dashboard/SlimFooter";
import { Footer } from "./Footer";
import { HeaderLayout } from "./Header/Header";
import { SideMenuLayout } from "./SideMenuLayout";
import { ToSWrapper } from "./ToSWrapper";

export type NextPageWithLayout<P = unknown, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: React.ReactElement) => React.ReactNode;
};

export const getDefaultLayout = (page: React.ReactElement) => (
  <HeaderLayout>
    {page}
    <Footer />
  </HeaderLayout>
);

export const getDashboardLayout = (page: React.ReactElement) => (
  <HeaderLayout>
    <ToSWrapper>
      <SideMenuLayout
        items={[
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
  </HeaderLayout>
);

export const getAdminLayout = (page: React.ReactElement) => (
  <HeaderLayout>
    <SideMenuLayout
      items={[
        {
          labelID: "users",
          pathname: "/admin",
          icon: Users,
        },
        {
          labelID: "Messages",
          pathname: "/admin/messages",
          icon: MessageSquare,
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
      <Box>{page}</Box>
    </SideMenuLayout>
  </HeaderLayout>
);

export const noLayout = (page: React.ReactElement) => page;
