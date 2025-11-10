/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Configurações de imagem
  images: {
    domains: [
      'localhost',
      '127.0.0.1',
      // Adicionar outros domínios conforme necessário
    ],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Configurações de API
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ]
  },

  // Configurações de build
  typescript: {
    // Durante o desenvolvimento, não falhar no build por erros de tipo
    ignoreBuildErrors: false,
  },

  eslint: {
    // Durante o desenvolvimento, não falhar no build por erros de lint
    ignoreDuringBuilds: false,
  },

  // Configurações de performance
  poweredByHeader: false,
  generateEtags: false,

  // Headers de segurança
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig