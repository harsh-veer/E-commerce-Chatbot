import Link from 'next/link'

const featureList = [
  'AI Product Q&A',
  'No account required',
  'Product Management',
  'Semantic Search & Recommendations',
  'Instant answers from your catalog',
]

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="mx-auto max-w-5xl rounded-3xl border border-slate-800 bg-slate-900/90 p-10 shadow-glow">
        <div className="mb-8 space-y-4">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">AI-powered e-commerce bot</p>
          <h1 className="text-5xl font-semibold tracking-tight text-white">Product Q&A with Retrieval-Augmented Generation</h1>
          <p className="max-w-3xl text-base leading-7 text-slate-300">
            Ask product questions instantly without signing up. Get fast, accurate answers based on the catalog.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/chat" className="rounded-full bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
              Start Chatting
            </Link>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {featureList.map((feature) => (
            <div key={feature} className="rounded-3xl border border-slate-800 bg-slate-950 p-6">
              <h2 className="text-lg font-semibold text-white">{feature}</h2>
              <p className="mt-2 text-sm text-slate-400">Built to deliver immediate product answers without account friction.</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
