// https://nextjs.org/docs/basic-features/layouts

import type { NextPage } from "next";
import { FiBarChart2, FiLayout, FiMessageSquare, FiUsers } from "react-icons/fi";
import { Header } from "src/components/Header";

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
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
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
      ]}
    >
      {page}
    </SideMenuLayout>
    <Footer />
  </div>
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
