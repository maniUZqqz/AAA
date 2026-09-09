/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The panel and the API live on the Django side; the marketing site only
  // reads public endpoints (plans, showcase) so nothing here needs auth.
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
  },
  images: { remotePatterns: [{ protocol: "http", hostname: "127.0.0.1" }] },
};
export default nextConfig;
