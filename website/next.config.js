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
};

module.exports = nextConfig;
