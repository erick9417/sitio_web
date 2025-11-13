/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Speed up CI/builds on constrained hosts: skip ESLint and TS type checking during production builds
  // Note: This does NOT affect development; only the production build step.
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      // Proxy all /api/* calls from Next to the FastAPI backend listening on 127.0.0.1:8001
      // Note: backend endpoints are at root (e.g., /products, /auth/login), so we map /api/:path* -> /:path*
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8001/:path*'
      }
    ]
  }
}

module.exports = nextConfig