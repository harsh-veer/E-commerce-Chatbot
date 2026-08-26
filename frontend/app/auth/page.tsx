"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function AuthIndex() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/chat")
  }, [router])

  return (
    <main className="min-h-[calc(100vh-80px)] px-6 py-12 flex items-center justify-center text-center">
      <div className="glass-panel w-full max-w-md rounded-3xl p-10 space-y-4">
        <div className="text-3xl">🚀</div>
        <h2 className="text-xl font-bold text-white">No Login Required!</h2>
        <p className="text-xs text-slate-400">All features are open. Redirecting you to the AI Assistant...</p>
      </div>
    </main>
  )
}
