import './globals.css'
import type { Metadata } from 'next'
import { AuthProvider } from '@/context/AuthContext'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: 'E-Commerce - AI-Powered Shopping Assistant',
  description: 'AI product Q&A bot for e-commerce with retrieval augmented generation.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="flex min-h-screen flex-col bg-slate-950 text-slate-100 font-sans">
        <AuthProvider>
          <Navbar />
          <div className="flex-1">{children}</div>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  )
}

