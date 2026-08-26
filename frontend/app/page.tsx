import Link from 'next/link'

const featureList = [
  {
    title: 'Instant Product Answers',
    desc: 'Get precise tech specifications, compatibility details, and usage guides in milliseconds using vector search.',
    icon: '⚡',
    gradient: 'from-cyan-500/20 to-blue-500/20',
    border: 'border-cyan-500/30',
  },
  {
    title: 'RAG Hybrid Search',
    desc: 'Powered by LangChain & FAISS vector stores to retrieve exact answers directly from the official store catalog.',
    icon: '🧠',
    gradient: 'from-purple-500/20 to-indigo-500/20',
    border: 'border-purple-500/30',
  },
  {
    title: 'Zero Friction Access',
    desc: 'Ask product questions immediately without mandatory account registration or cumbersome signups.',
    icon: '🚀',
    gradient: 'from-emerald-500/20 to-teal-500/20',
    border: 'border-emerald-500/30',
  },
]

const sampleQueries = [
  "Which laptops have 16GB RAM and battery life over 10 hours?",
  "What is the warranty policy on noise-canceling headphones?",
  "Recommend a smartwatch suitable for swimming under ₹25,000.",
]

export default function Home() {
  return (
    <main className="min-h-[calc(100vh-80px)] px-6 py-12">
      <div className="mx-auto max-w-6xl space-y-16">
        {/* Hero Banner */}
        <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/60 p-8 md:p-14 shadow-2xl backdrop-blur-xl">
          <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-indigo-500/10 blur-3xl" />
          
          <div className="relative z-10 space-y-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 text-xs font-semibold text-cyan-400">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              AI Retrieval-Augmented Generation Active
            </div>
            
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl sm:leading-none">
              Shop Smarter with <br />
              <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
                Intelligent Product Q&A
              </span>
            </h1>
            
            <p className="text-lg text-slate-300 leading-relaxed">
              Ask complex questions about tech specifications, compatibility, warranties, and stock availability. 
              Get accurate, contextual answers instantly from our knowledge store.
            </p>
            
            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 px-7 py-3.5 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/25 transition hover:brightness-110 hover:scale-105"
              >
                <span>Launch AI Assistant</span>
                <span className="text-base">💬</span>
              </Link>
              <Link
                href="/products"
                className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/80 px-7 py-3.5 text-sm font-semibold text-slate-200 transition hover:border-cyan-500/50 hover:bg-slate-800"
              >
                <span>Browse Catalog</span>
                <span className="text-base">🛍️</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Sample Prompt Shortcuts */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">
            Popular AI Inquiries
          </h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {sampleQueries.map((query, idx) => (
              <Link
                key={idx}
                href={`/chat?q=${encodeURIComponent(query)}`}
                className="glass-card rounded-2xl p-4 flex items-center justify-between text-xs text-slate-300 hover:text-cyan-300 group"
              >
                <span>"{query}"</span>
                <span className="text-cyan-400 transition-transform group-hover:translate-x-1">→</span>
              </Link>
            ))}
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid gap-6 sm:grid-cols-2">
          {featureList.map((f) => (
            <div
              key={f.title}
              className={`glass-card rounded-3xl border ${f.border} p-8 flex flex-col justify-between space-y-4`}
            >
              <div className="flex items-center gap-4">
                <div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${f.gradient} text-2xl`}>
                  {f.icon}
                </div>
                <h3 className="text-xl font-bold text-white">{f.title}</h3>
              </div>
              <p className="text-sm leading-relaxed text-slate-300">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Stats Banner */}
        <div className="rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 p-8 shadow-xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <p className="text-3xl font-extrabold text-cyan-400">100%</p>
              <p className="mt-1 text-xs text-slate-400">Catalog Context Accuracy</p>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-indigo-400">&lt; 300ms</p>
              <p className="mt-1 text-xs text-slate-400">FAISS Vector Search</p>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-emerald-400">24/7</p>
              <p className="mt-1 text-xs text-slate-400">Automated Q&A Response</p>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-amber-400">MongoDB</p>
              <p className="mt-1 text-xs text-slate-400">Real-time Catalog Sync</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
