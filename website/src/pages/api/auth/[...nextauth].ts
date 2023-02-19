import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { boolean } from "boolean";
import { generateUsername } from "friendly-username-generator";
import { NextApiRequest, NextApiResponse } from "next";
import type { AuthOptions } from "next-auth";
import NextAuth from "next-auth";
import { Provider } from "next-auth/providers";
import CredentialsProvider from "next-auth/providers/credentials";
import DiscordProvider from "next-auth/providers/discord";
import EmailProvider from "next-auth/providers/email";
import { checkCaptcha } from "src/lib/captcha";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { BackendUserCore } from "src/types/Users";

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

const moderatorUserMap = process.env.MODERATOR_USERS.split(",").reduce((result, entry) => {
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
  session: {
    strategy: "jwt",
  },
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
      session.user.tosAcceptanceDate = token.tosAcceptanceDate;
      return session;
    },
    /**
     * When creating a token, fetch the user's role and inject it in the token.
     * This let's use forward the role to the session object.
     */
    async jwt({ token }) {
      const { isNew, name, role, accounts, id } = await prisma.user.findUnique({
        where: { id: token.sub },
        select: { name: true, role: true, isNew: true, accounts: true, id: true },
      });

      // Note: This could be cleaner and merged with src/lib/users.ts
      const user: BackendUserCore = {
        id: accounts.length > 0 ? accounts[0].providerAccountId : id,
        display_name: name,
        auth_method: accounts.length > 0 ? accounts[0].provider : "local",
      };
      const oasstApiClient = createApiClientFromUser(user);

      let tosAcceptanceDate = null;
      try {
        /**
         * when first creating a new user, the python backend is not informed about it
         * so this call will return a 404
         *
         * in the frontend, when the user accepts the tos, we do a full refresh
         * which means this function will be called again.
         */
        tosAcceptanceDate = await oasstApiClient.fetch_tos_acceptance(user);
      } catch (err) {
        if (err.httpStatusCode !== 404) {
          throw err;
        }
      }

      token.name = name;
      token.role = role;
      token.isNew = isNew;
      token.tosAcceptanceDate = tosAcceptanceDate;
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
      const moderatorForAccountType = moderatorUserMap.get(account.provider);

      // Return early if there's no admin list.
      if (!adminForAccountType && !moderatorForAccountType) {
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

      if (moderatorForAccountType.has(account.providerAccountId)) {
        await prisma.user.update({
          data: {
            role: "moderator",
          },
          where: {
            id: user.id,
          },
        });
      }
    },
  },
};

export default function auth(req: NextApiRequest, res: NextApiResponse) {
  return NextAuth(req, res, {
    ...authOptions,
    callbacks: {
      ...authOptions.callbacks,
      async signIn({ account }) {
        const isVerifyEmail = req.url ? req.url.includes("/api/auth/callback/email") : false;

        if (account.provider !== "email" || !boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA) || isVerifyEmail) {
          return true;
        }

        if (account.provider === "email" && !boolean(process.env.ENABLE_EMAIL_SIGNIN)) {
          return false;
        }

        const captcha = req.body.captcha;

        const res = await checkCaptcha(captcha, getIp(req));

        if (res.success) {
          return true;
        }

        return "/auth/signin?error=InvalidCaptcha";
      },
    },
  });
}

const getIp = (req: NextApiRequest) => {
  try {
    // https://stackoverflow.com/questions/66111742/get-the-client-ip-on-nextjs-and-use-ssr
    const forwarded = req.headers["x-forwarded-for"];
    return typeof forwarded === "string" ? forwarded.split(/, /)[0] : req.socket.remoteAddress;
  } catch {
    return "";
  }
};
