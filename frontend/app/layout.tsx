import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Veo area recommender',
  description: 'Persona-weighted ranking of London postcode districts. Prototype: some data is synthetic.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
