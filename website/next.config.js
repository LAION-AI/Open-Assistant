/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  experimental: {
    /* Disabling this for now only because it causes a warning in the console that cannot be silenced for eslint
       If this can be resolved, we should re-enable this.
    */
    // scrollRestoration: true,
  },
};

module.exports = nextConfig;
