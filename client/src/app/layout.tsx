import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import '../styles/globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'IA Generativa para Conteúdo de Mídia Social',
    template: '%s | IA Generativa para Conteúdo'
  },
  description: 'Sistema de geração automatizada de conteúdo para Instagram utilizando Inteligência Artificial Generativa com arquitetura RAG.',
  keywords: [
    'inteligência artificial',
    'IA generativa',
    'Instagram',
    'conteúdo',
    'mídia social',
    'marketing digital',
    'automação',
    'RAG',
    'TCC'
  ],
  authors: [{ name: 'Estudante - Sistemas de Informação' }],
  creator: 'Estudante - Sistemas de Informação',
  publisher: 'Universidade',
  robots: {
    index: false, // Para protótipo acadêmico
    follow: false,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: process.env.NEXT_PUBLIC_APP_URL,
    title: 'IA Generativa para Conteúdo de Mídia Social',
    description: 'Sistema de geração automatizada de conteúdo para Instagram utilizando IA Generativa',
    siteName: 'IA Generativa para Conteúdo',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'IA Generativa para Conteúdo de Mídia Social',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IA Generativa para Conteúdo de Mídia Social',
    description: 'Sistema de geração automatizada de conteúdo para Instagram utilizando IA Generativa',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            <main className="flex-1">
              {children}
            </main>
          </div>
          <Toaster
            position="bottom-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'hsl(var(--card))',
                color: 'hsl(var(--card-foreground))',
                border: '1px solid hsl(var(--border))',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}