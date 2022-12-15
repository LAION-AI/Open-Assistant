import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";
import EmailProvider from "next-auth/providers/email";
import { PrismaAdapter } from "@next-auth/prisma-adapter";

import prisma from "../../../lib/prismadb";

export const authOptions = {
  // Ensure we can store user data in a database.
  adapter: PrismaAdapter(prisma),
  providers: [
    // Register a Discord auth method.
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID,
      clientSecret: process.env.DISCORD_CLIENT_SECRET,
    }),
    // Register an email magic link auth method.
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST,
        port: process.env.EMAIL_SERVER_PORT,
        auth: {
          user: process.env.EMAIL_SERVER_USER,
          pass: process.env.EMAIL_SERVER_PASSWORD,
        },
      },
      from: process.env.EMAIL_FROM,
    }),
  ],
  callbacks: {
    /**
     * Includes the raw user id in the session object.
     */
    async session({ session, token, user }) {
      session.user.id = user.id;
      return session;
    },
  },
  events: {
    /**
     * When a new user signs in, we register them with the Labeler backend.
     */
    async signIn({ user, account, profile, isNewUser }) {
      if (!isNewUser) {
        return;
      }
      try {
        // Register the new user with the Labeler Backend.
        const res = await fetch(`${process.env.FASTAPI_URL}/api/v1/labelers`, {
          method: "POST",
          headers: {
            "X-API-Key": process.env.FASTAPI_KEY,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            discord_username: user.id,
            display_name: user.name || user.email,
            is_enabled: true,
            notes: account.provider,
          }),
        });
        if (res.status !== 200) {
          console.error(res.statusText);
          return;
        }
        // Update the User entry with the Labeler Backend's ID so we can
        // reference it later.
        const { id: labelerId } = await res.json();
        await prisma.user.update({
          where: { id: user.id },
          data: {
            labelerId,
          },
        });
      } catch (error) {
        console.error(error);
      }
    },
  },
};

export default NextAuth(authOptions);
