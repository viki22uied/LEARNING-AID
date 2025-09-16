import type React from "react"
import type { Metadata } from "next"
import { GeistMono } from "geist/font/mono"
import { Work_Sans, Open_Sans } from "next/font/google"
import "./globals.css"

const workSans = Work_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-work-sans",
})

const openSans = Open_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-open-sans",
})

export const metadata: Metadata = {
  title: "AI Learning Aid - Transform Voice Notes into Smart Study Guides",
  description:
    "Upload voice notes, get AI-powered transcriptions, extract key concepts, and discover personalized learning resources.",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <style>{`
html {
  font-family: ${openSans.style.fontFamily};
  --font-sans: ${openSans.variable};
  --font-mono: ${GeistMono.variable};
  --font-heading: ${workSans.variable};
}
        `}</style>
      </head>
      <body className={`${workSans.variable} ${openSans.variable} ${GeistMono.variable}`}>{children}</body>
    </html>
  )
}
