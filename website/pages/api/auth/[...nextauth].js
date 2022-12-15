import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";
import { PrismaAdapter } from "@next-auth/prisma-adapter";

import prisma from "../../../lib/prismadb";

export const authOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID,
      clientSecret: process.env.DISCORD_CLIENT_SECRET,
    }),
  ],
  callbacks: {
    async session({ session, token, user }) {
      session.user.sub = token.sub;
      return session;
    },
  },
};

export default NextAuth(authOptions);
