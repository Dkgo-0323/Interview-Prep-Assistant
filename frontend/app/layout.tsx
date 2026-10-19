import type { Metadata, Viewport } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { SiteNav } from "@/components/site-nav"
import "./globals.css"

export const metadata: Metadata = {
  title: 'Interview Prep Assistant',
  description: '上传职位描述和简历，开始你的面试准备',
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh" className={`${GeistSans.variable} ${GeistMono.variable} bg-background`} suppressHydrationWarning>
      <body className="font-sans antialiased">
        <SiteNav />
        {children}
      </body>
    </html>
  )
}

