import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { boolean } from "boolean";
import { NextApiRequest, NextApiResponse } from "next";
import type { AuthOptions } from "next-auth";
import NextAuth from "next-auth";
import { Provider } from "next-auth/providers";
import CredentialsProvider from "next-auth/providers/credentials";
import DiscordProvider from "next-auth/providers/discord";
import EmailProvider from "next-auth/providers/email";
import { checkCaptcha } from "src/lib/captcha";
import prisma from "src/lib/prismadb";
import { generateUsername } from "unique-username-generator";

const providers: Provider[] = [];

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
        role: { label: "Role", type: "text" },
      },
      async authorize(credentials) {
        const user = {
          id: credentials.username,
          name: credentials.username,
          role: credentials.role,
        };
        // save the user to the database
        await prisma.user.upsert({
          where: {
            id: user.id,
          },
          update: user,
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

const authOptions: AuthOptions = {
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
      session.user.isNew = token.isNew;
      session.user.name = token.name;
      return session;
    },
    /**
     * When creating a token, fetch the user's role and inject it in the token.
     * This let's use forward the role to the session object.
     */
    async jwt({ token }) {
      const { isNew, name, role } = await prisma.user.findUnique({
        where: { id: token.sub },
        select: { name: true, role: true, isNew: true },
      });
      token.name = name;
      token.role = role;
      token.isNew = isNew;
      return token;
    },
  },
  events: {
    /**
     * Update the user's role after they have successfully signed in
     */
    async signIn({ user, account, isNewUser }) {
      if (isNewUser && account.provider === "email") {
        await prisma.user.update({
          data: {
            name: generateUsername(),
          },
          where: {
            id: user.id,
          },
        });
      }

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

export default function auth(req: NextApiRequest, res: NextApiResponse) {
  return NextAuth(req, res, {
    ...authOptions,
    callbacks: {
      ...authOptions.callbacks,
      async signIn({ account }) {
        if (account.provider !== "email" || !boolean(process.env.NEXT_PUBLIC_ENABLE_EMAIL_SIGNIN_CAPTCHA)) {
          return true;
        }

        const captcha = getBody(req.body)?.captcha;
        // https://stackoverflow.com/questions/66111742/get-the-client-ip-on-nextjs-and-use-ssr
        const forwarded = req.headers["x-forwarded-for"];
        const ip = typeof forwarded === "string" ? forwarded.split(/, /)[0] : req.socket.remoteAddress;

        const res = await checkCaptcha(captcha, ip);

        if (res.success) {
          return true;
        }

        return "/auth/signin?error=InvalidCaptcha";
      },
    },
  });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getBody = (req: NextApiRequest): Record<string, any> => {
  return req.headers["content-type"]?.includes("application/x-www-form-urlencoded") ? req.body : req.query;
};
