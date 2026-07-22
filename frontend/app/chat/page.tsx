"use client"

import { useState } from "react"
import api from "@/services/api"
import PageHeader from "@/components/PageHeader"

interface ChatEntry {
  question: string
  answer: string
}

export default function ChatPage() {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<ChatEntry[]>([])
  const [status, setStatus] = useState("Ready to chat")

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!question.trim()) {
      return
    }

    setStatus("Thinking...")
    const reply = { question, answer: "" }
    setMessages((current) => [...current, reply])

    try {
      console.log("Sending chat request", question)
      const response = await api.post("/chat/", { question })
      console.log("Chat response", response)
      const answer = response.data?.answer ?? "No answer returned"
      setMessages((current) => current.map((message, index) => (index === current.length - 1 ? { ...message, answer } : message)))
      setQuestion("")
      setStatus("Ready to chat")
    } catch (err) {
      console.error("Chat request failed", err)
      setStatus("Unable to load answer. Try again.")
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <div className="mx-auto max-w-4xl rounded-3xl border border-slate-800 bg-slate-900/95 p-10 shadow-glow">
        <div className="pb-8">
          <PageHeader title="Product Q&A" description="Ask about product features, availability, or recommendations instantly." />
        </div>
        <form className="mb-6 space-y-4" onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a product question..."
            className="min-h-[120px] w-full rounded-3xl border border-slate-700 bg-slate-950 px-4 py-4 text-slate-100 outline-none resize-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
          />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-sm text-slate-400">{status}</span>
            <button type="submit" className="rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
              Send Question
            </button>
          </div>
        </form>
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div key={index} className="rounded-3xl border border-slate-800 bg-slate-950 p-6">
              <p className="text-sm uppercase tracking-[0.2em] text-cyan-400">Question</p>
              <p className="mt-2 text-base text-slate-100">{message.question}</p>
              <div className="mt-4 rounded-3xl border border-slate-800 bg-slate-900 p-4">
                <p className="text-sm uppercase tracking-[0.2em] text-emerald-400">Answer</p>
                <p className="mt-2 text-base text-slate-200">{message.answer || "Waiting for response..."}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
