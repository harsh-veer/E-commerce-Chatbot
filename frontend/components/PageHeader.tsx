interface PageHeaderProps {
  title: string
  description: string
}

export default function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-8 space-y-3">
      <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">E-Commerce Chatbot</p>
      <h1 className="text-4xl font-semibold text-white">{title}</h1>
      <p className="max-w-3xl text-slate-400">{description}</p>
    </div>
  )
}
