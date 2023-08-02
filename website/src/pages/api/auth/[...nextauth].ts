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
import GoogleProvider from "next-auth/providers/google";
import { checkCaptcha } from "src/lib/captcha";
import { createApiClientFromUser } from "src/lib/oasst_client_factory";
import prisma from "src/lib/prismadb";
import { convertToBackendUserCore } from "src/lib/users";

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

if (process.env.GOOGLE_CLIENT_ID) {
  providers.push(
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      authorization: {
        // NOTE: adding this will case the app to ask the user
        // to login every time, might be a bit annoying
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
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
const adminUserMap: Map<string, Set<string>> = process.env.ADMIN_USERS.split(",").reduce((result, entry) => {
  const [authType, id] = entry.split(":");
  const s = result.get(authType) || new Set();
  s.add(id);
  result.set(authType, s);
  return result;
}, new Map());

const moderatorUserMap: Map<string, Set<string>> = process.env.MODERATOR_USERS.split(",").reduce((result, entry) => {
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
      session.user.image = token.picture;
      session.user.tosAcceptanceDate = token.tosAcceptanceDate;
      session.inference = { isAuthenticated: !!token.inferenceTokens };
      return session;
    },
  },
  events: {
    /**
     * Update the user after they have successfully signed in
     */
    async signIn({ user, account, isNewUser, profile }) {
      // any values that might be updated in the user profile
      const toBeUpdated: Partial<{ name: string; role: string; image: string }> = {};

      if (isNewUser && account.provider === "email" && !user.name) {
        // only generate a username if the user is new and they signed up with email and they don't have a name
        // although the name already assigned in the jwt callback, this is to ensure nothing breaks, and we should never reach here.
        toBeUpdated.name = generateUsername();
      }

      // update image
      if (profile && profile.image) {
        toBeUpdated.image = profile.image;
      }

      // update roles
      // TODO(#236): Reduce the number of times we update the role field.
      if (moderatorUserMap.get(account.provider)?.has(account.providerAccountId)) {
        toBeUpdated.role = "moderator";
      }
      if (adminUserMap.get(account.provider)?.has(account.providerAccountId)) {
        toBeUpdated.role = "admin";
      }

      if (Object.keys(toBeUpdated).length > 0) {
        await prisma.user.update({
          where: { id: user.id },
          data: toBeUpdated,
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
      /**
       * When creating a token, fetch the user's role and inject it in the token.
       * This let's use forward the role to the session object.
       */
      async jwt({ token }) {
        const frontendUser = await prisma.user.findUnique({
          where: { id: token.sub },
          select: { name: true, role: true, isNew: true, accounts: true, image: true, id: true },
        });

        if (!frontendUser) {
          // should never reach here
          throw new Error("User not found");
        }

        // TODO avoid duplicate logic with the signIn event
        if (frontendUser.isNew && !frontendUser.name) {
          // jwt callback is called before signIn event, so we need to assign the name here otherwise the backend will refuse the request
          frontendUser.name = generateUsername();
          await prisma.user.update({
            data: {
              name: frontendUser.name,
            },
            where: {
              id: frontendUser.id,
            },
          });
        }

        token.name = frontendUser.name;
        token.role = frontendUser.role;
        token.isNew = frontendUser.isNew;
        token.picture = frontendUser.image;

        // these are immutable once assigned
        if (!token.tosAcceptanceDate || !token.backendUserId) {
          const backendUser = convertToBackendUserCore(frontendUser);
          const oasstApiClient = createApiClientFromUser(backendUser);

          const user = await oasstApiClient.upsert_frontend_user(backendUser);
          token.backendUserId = user.user_id;
          token.tosAcceptanceDate = user.tos_acceptance_date;
        }
        return token;
      },
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
