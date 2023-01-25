import { NextResponse } from "next/server";
import { NextRequestWithAuth, withAuth } from "next-auth/middleware";

import { checkCaptcha } from "./lib/captcha";
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
    "/api/auth/signin/email",
  ],
};

const middleware = async (req: NextRequestWithAuth) => {
  if (req.method === "POST" && req.nextUrl.pathname === "/api/auth/signin/email") {
    const data = await getBody(req);
    const res = await checkCaptcha(data?.captcha, req.ip);

    if (res.success) {
      return NextResponse.next();
    }

    const url = req.nextUrl.clone();
    url.pathname = "/api/auth/invalid-captcha";

    return NextResponse.redirect(url);
  }

  return withAuth(req);
};

async function getBody(req: Request): Promise<Record<string, any> | undefined> {
  if (!("body" in req) || !req.body || req.method !== "POST") return;

  const contentType = req.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return await req.json();
  } else if (contentType?.includes("application/x-www-form-urlencoded")) {
    const params = new URLSearchParams(await req.text());
    return Object.fromEntries(params);
  }
}

export default middleware;
