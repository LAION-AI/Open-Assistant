import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { boolean } from "boolean";
import type { AuthOptions } from "next-auth";
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import DiscordProvider from "next-auth/providers/discord";
import EmailProvider from "next-auth/providers/email";
import prisma from "src/lib/prismadb";

const providers = [];

// Register an email magic link auth method.
providers.push(
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
  })
);

if (process.env.DISCORD_CLIENT_ID) {
  providers.push(
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID,
      clientSecret: process.env.DISCORD_CLIENT_SECRET,
    })
  );
}

if (boolean(process.env.DEBUG_LOGIN) || process.env.NODE_ENV === "development") {
  providers.push(
    CredentialsProvider({
      name: "Debug Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
      },
      async authorize(credentials) {
        const user = {
          id: credentials.username,
          name: credentials.username,
        };
        // save the user to the database
        await prisma.user.upsert({
          where: {
            id: user.id,
          },
          update: {},
          create: user,
        });
        return user;
      },
    })
  );
}

export const authOptions: AuthOptions = {
  // Ensure we can store user data in a database.
  adapter: PrismaAdapter(prisma),
  providers,
  pages: {
    signIn: "/auth/signin",
    verifyRequest: "/auth/verify",
    // error: "/auth/error", -Will be used later
  },
  session: {
    strategy: "jwt",
  },
};

export default NextAuth(authOptions);
