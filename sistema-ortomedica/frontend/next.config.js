/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
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