export { default } from "next-auth/middleware";

/**
 * Guards all pages under `/grading` and redirects them to the sign in page.
 */
export const config = {
  matcher: ["/create/:path*", "/evaluate/:path*", "/account/:path*", "/dashboard"],
};
