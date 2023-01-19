// https://nextjs.org/docs/basic-features/layouts

import { Box, Grid } from "@chakra-ui/react";
import type { NextPage } from "next";
import { FiAlertTriangle, FiBarChart2, FiLayout, FiMessageSquare, FiUsers } from "react-icons/fi";
import { FaQuestionCircle } from "react-icons/fa";

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
    <Header transparent={true} />
    {page}
    <Footer />
  </div>
);

export const getDashboardLayout = (page: React.ReactElement) => (
  <Grid templateRows="min-content 1fr" h="full">
    <Header transparent={true} />
    <SideMenuLayout
      menuButtonOptions={[
        {
          label: "Dashboard",
          pathname: "/dashboard",
          desc: "Dashboard Home",
          icon: FiLayout,
        },
        {
          label: "Messages",
          pathname: "/messages",
          desc: "Messages Dashboard",
          icon: FiMessageSquare,
        },
        {
          label: "Leaderboard",
          pathname: "/leaderboard",
          desc: "User Leaderboard",
          icon: FiBarChart2,
        },
        {
          label: "Guide",
          pathname: "/guide",
          desc: "Guide to the App",
          icon: FaQuestionCircle,
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
    <Header transparent={true} />
    <SideMenuLayout
      menuButtonOptions={[
        {
          label: "Users",
          pathname: "/admin",
          desc: "Users Dashboard",
          icon: FiUsers,
        },
      ]}
    >
      {page}
    </SideMenuLayout>
  </div>
);

export const noLayout = (page: React.ReactElement) => page;
