import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'BetStats Trader - Análise Premium de Apostas',
  description: 'Plataforma premium de análise estatística para apostas esportivas',
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
