import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
})

export const metadata: Metadata = {
    title: 'Parallax AI | Narrative Intelligence',
    description: 'AI-powered narrative analysis and bias detection platform',
    keywords: ['AI', 'narrative analysis', 'bias detection', 'news analysis'],
    authors: [{ name: 'Hyder Ahmed' }],
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className={inter.variable}>
            <body className="antialiased min-h-screen flex flex-col">
                <div className="frost-background" aria-hidden="true" />
                <Providers>
                    {children}
                </Providers>
            </body>
        </html>
    )
}

