const { i18n } = require("./next-i18next.config");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.discordapp.com",
      },
      {
        protocol: "https",
        hostname: "api.dicebear.com",
      },
    ],
  },
  experimental: {
    /* Disabling this for now only because it causes a warning in the console that cannot be silenced for eslint
       If this can be resolved, we should re-enable this.
    */
    // scrollRestoration: true,
  },
  i18n,
  eslint: {
    ignoreDuringBuilds: true,
  },
  async redirects() {
    if (process.env.MAINTENANCE_MODE !== "true") {
      return [];
    }
    return [
      {
        source: "/",
        destination: "/brb",
        permanent: false,
      },
      {
        source: "/dashboard",
        destination: "/brb",
        permanent: false,
      },
      {
        source: `/tasks/:task`,
        destination: "/brb",
        permanent: false,
      },
      {
        source: "/leaderboard",
        destination: "/brb",
        permanent: false,
      },
    ];
  },
};

const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
  openAnalyzer: true,
});

module.exports = withBundleAnalyzer(nextConfig);
