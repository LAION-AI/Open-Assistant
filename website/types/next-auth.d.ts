import NextAuth, { DefaultSession } from "next-auth";
import { JWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    user: {
      /** The user's role. */
      role: string;
      /** True when the user is new. */
      isNew: boolean;
    } & DefaultSession["user"];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    /** The user's role. */
    role?: string;
    /** True when the user is new. */
    isNew?: boolean;
  }
}
