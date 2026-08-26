import ReactMarkdown from 'react-markdown'

interface MarkdownRendererProps {
  content: string
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="text-sm leading-relaxed text-slate-200 space-y-2">
      <ReactMarkdown
        components={{
          h1: ({ children }) => <h1 className="text-lg font-bold text-cyan-300 mt-4 mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-bold text-cyan-300 mt-3 mb-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-bold text-cyan-300 mt-3 mb-1">{children}</h3>,
          strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
          em: ({ children }) => <em className="italic text-slate-300">{children}</em>,
          p: ({ children }) => <p className="mb-2 leading-relaxed">{children}</p>,
          ul: ({ children }) => <ul className="list-disc pl-5 space-y-1 my-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 space-y-1 my-2">{children}</ol>,
          li: ({ children }) => <li className="text-slate-200">{children}</li>,
          hr: () => <hr className="my-3 border-slate-800" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
