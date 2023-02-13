export { default } from "next-auth/middleware";

/**
 * Guards these pages and redirects them to the sign in page.
 */
export const config = {
  matcher: [
    "/create/:path*",
    "/evaluate/:path*",
    "/label/:path*",
    "/account/:path*",
    "/dashboard",
    "/admin/:path*",
    "/tasks/:path*",
    "/leaderboard",
    "/messages/:path*",
    "/chat",
  ],
};
