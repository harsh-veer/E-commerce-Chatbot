import Link from 'next/link'

export default function AuthIndex() {
  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <div className="mx-auto max-w-2xl rounded-3xl border border-slate-800 bg-slate-900/95 p-10 shadow-glow">
        <h1 className="text-4xl font-semibold text-white">Authentication</h1>
        <p className="mt-4 text-slate-400">Use the links below to login or create an account.</p>
        <div className="mt-8 flex flex-col gap-4 sm:flex-row">
          <Link href="/auth/login" className="rounded-full bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
            Login
          </Link>
          <Link href="/auth/signup" className="rounded-full border border-slate-600 px-5 py-3 text-sm text-slate-100 transition hover:border-slate-400">
            Sign up
          </Link>
        </div>
      </div>
    </main>
  )
}
