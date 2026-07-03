import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The API origin is read server-side only (in BFF route handlers), so it is
  // never exposed to the browser. Set API_BASE_URL in the hosting platform.
};

export default nextConfig;
