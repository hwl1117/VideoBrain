/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用严格模式
  reactStrictMode: true,

  // 环境变量 - 优先使用 NEXT_PUBLIC_API_URL
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000',
  },

  // API代理配置 - 仅在本地开发时使用
  async rewrites() {
    // 在 Vercel 生产环境中，API 调用直接指向后端服务
    if (process.env.VERCEL) {
      return []
    }
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },

  // 图片域名配置
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'https', hostname: 'via.placeholder.com' },
      { protocol: 'https', hostname: '**.vercel.app' },
      { protocol: 'https', hostname: '**.onrender.com' },
      { protocol: 'https', hostname: '**.railway.app' },
      { protocol: 'https', hostname: '**.fly.dev' },
    ],
    unoptimized: true, // Vercel 部署时可能需要
  },

  turbopack: {
    root: __dirname,
  },

  // 输出配置
  output: 'standalone',

  // 实验性功能
  experimental: {
    // 优化包大小
    optimizePackageImports: ['lucide-react'],
  },
}

module.exports = nextConfig
