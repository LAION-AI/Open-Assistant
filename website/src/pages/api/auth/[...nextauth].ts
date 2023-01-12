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

// Create a map of provider types to a set of admin user identifiers based on
// the environment variables.  We assume the list is separated by ',' and each
// entry is separated by ':'.
const adminUserMap = process.env.ADMIN_USERS.split(",").reduce((result, entry) => {
  const [authType, id] = entry.split(":");
  const s = result.get(authType) || new Set();
  s.add(id);
  result.set(authType, s);
  return result;
}, new Map());

export const authOptions: AuthOptions = {
  // Ensure we can store user data in a database.
  adapter: PrismaAdapter(prisma),
  providers,
  pages: {
    signIn: "/auth/signin",
    verifyRequest: "/auth/verify",
    // error: "/auth/error", -Will be used later
  },
  callbacks: {
    /**
     * Ensure we propagate the user's role when creating the session from the
     * token.
     */
    async session({ session, token }) {
      session.user.role = token.role;
      return session;
    },
    /**
     * When creating a token, fetch the user's role and inject it in the token.
     * This let's use forward the role to the session object.
     */
    async jwt({ token }) {
      const { role } = await prisma.user.findUnique({
        where: { id: token.sub },
        select: { role: true },
      });
      token.role = role;
      return token;
    },
  },
  events: {
    /**
     * Update the user's role after they have successfully signed in
     */
    async signIn({ user, account }) {
      // Get the admin list for the user's auth type.
      const adminForAccountType = adminUserMap.get(account.provider);

      // Return early if there's no admin list.
      if (!adminForAccountType) {
        return;
      }

      // TODO(#236): Reduce the number of times we update the role field.

      // Update the database if the user is an admin.
      if (adminForAccountType.has(account.providerAccountId)) {
        await prisma.user.update({
          data: {
            role: "admin",
          },
          where: {
            id: user.id,
          },
        });
      }
    },
  },
  session: {
    strategy: "jwt",
  },
};

export default NextAuth(authOptions);
