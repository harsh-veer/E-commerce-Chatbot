"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

export default function Navbar() {
  const pathname = usePathname()

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Products", path: "/products" },
    { name: "AI Assistant", path: "/chat" },
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 shadow-lg shadow-cyan-500/25 group-hover:scale-105 group-hover:shadow-cyan-500/40 transition-all duration-300">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-400"></span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xl font-black tracking-tight text-white group-hover:text-cyan-400 transition-colors">
              E-Commerce
            </span>
            <span className="rounded-md bg-cyan-500/10 px-2 py-0.5 text-[10px] font-bold text-cyan-400 border border-cyan-500/25 uppercase tracking-wider">
              AI STORE
            </span>
          </div>
        </Link>

        {/* Center Navigation */}
        <nav className="flex items-center gap-1 rounded-full border border-slate-800 bg-slate-900/60 p-1.5 backdrop-blur-sm">
          {navLinks.map((link) => {
            const isActive = pathname === link.path
            return (
              <Link
                key={link.path}
                href={link.path}
                className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-950 shadow-md font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                {link.name}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
