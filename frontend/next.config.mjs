/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  basePath: "/autonomous-task-agent",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
