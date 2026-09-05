import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PlatformPulse — Developer Platform Command Center',
  description: 'Interactive developer-platform product lab for discovery, golden paths, reliability, experimentation, and AI governance.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
