import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Veo - Smart Housing Recommendations',
  description: 'AI-powered housing recommendations for London',
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
