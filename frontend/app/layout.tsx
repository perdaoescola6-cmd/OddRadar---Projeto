import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: 'BetFaro - Aposte como um insider 🐕',
  description: 'Dados reais, análises profundas e as melhores oportunidades do dia. Plataforma premium de análise estatística para apostas esportivas.',
  keywords: ['apostas esportivas', 'análise estatística', 'futebol', 'odds', 'value bet', 'picks'],
  authors: [{ name: 'BetFaro' }],
  openGraph: {
    title: 'BetFaro - Aposte como um insider 🐕',
    description: 'Dados reais, análises profundas e as melhores oportunidades do dia.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-dark-bg text-dark-text`}>
        {children}
      </body>
    </html>
  )
}
