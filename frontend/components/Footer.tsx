import Link from "next/link"

export default function Footer() {
  return (
    <footer className="w-full border-t border-slate-800 bg-slate-950/90 py-10 text-slate-400">
      <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-md">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-200">
            E-Commerce &copy; {new Date().getFullYear()} - AI-Powered Shopping Platform
          </span>
        </div>
        <div className="flex items-center gap-6 text-xs text-slate-400">
          <Link href="/products" className="hover:text-cyan-400 transition">
            Product Catalog
          </Link>
          <Link href="/chat" className="hover:text-cyan-400 transition">
            AI Assistant
          </Link>
        </div>
      </div>
    </footer>
  )
}
