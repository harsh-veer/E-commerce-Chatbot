"use client"

import { useEffect, useRef, useState, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { getChatHistory, sendChatQuestionStream, clearChatHistory } from "@/services/api"
import { ChatMessage } from "@/types"
import PageHeader from "@/components/PageHeader"
import MarkdownRenderer from "@/components/MarkdownRenderer"


const quickPrompts = [
  "Which laptops have 16GB RAM and long battery life?",
  "What smartwatches have fitness tracking under $300?",
  "Compare noise canceling wireless headphones.",
  "Tell me about return policy and product warranty.",
]

function ChatContent() {
  const searchParams = useSearchParams()
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<Partial<ChatMessage>[]>([])
  const [loading, setLoading] = useState(false)
  const [fetchingHistory, setFetchingHistory] = useState(true)
  const [status, setStatus] = useState("Ready to assist")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    async function loadHistory() {
      try {
        setFetchingHistory(true)
        const history = await getChatHistory()
        if (history && history.length > 0) {
          // Backend returns newest first; reverse for chronological chat stream
          setMessages(history.reverse())
        }
      } catch (err) {
        console.error("Could not fetch chat history", err)
      } finally {
        setFetchingHistory(false)
      }
    }
    loadHistory()
  }, [])

  const handleClearHistory = async () => {
    try {
      await clearChatHistory()
      setMessages([])
      setStatus("Chat history cleared")
    } catch (err) {
      console.error("Failed to clear chat history", err)
    }
  }

  // Auto handle URL query param `?q=...`
  useEffect(() => {
    const qParam = searchParams.get("q")
    if (qParam && !loading) {
      setQuestion(qParam)
    }
  }, [searchParams])

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || question
    if (!q.trim() || loading) return

    setLoading(true)
    setStatus("Thinking & generating AI answer...")
    const userMsg: Partial<ChatMessage> = {
      question: q,
      answer: "",
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    if (!textToSend) setQuestion("")

    try {
      let accumulatedAnswer = ""
      await sendChatQuestionStream(q, (chunk) => {
        accumulatedAnswer += chunk
        setMessages((prev) =>
          prev.map((msg, idx) =>
            idx === prev.length - 1 ? { ...msg, answer: accumulatedAnswer } : msg
          )
        )
      })
      setStatus("Ready to assist")
    } catch (err) {
      console.error("Chat API call failed", err)
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === prev.length - 1
            ? { ...msg, answer: "⚠️ Sorry, I encountered an issue retrieving an answer. Please verify the backend service is running." }
            : msg
        )
      )
      setStatus("Error loading response")
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSend()
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex justify-between items-center">
        <PageHeader
          title="AI Product Assistant"
          description="Ask questions about product details, specifications, comparisons, or recommendations."
        />
      </div>

      {/* Suggestion Chips & Clear Chat Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Suggested Inquiries</span>
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuestion(prompt)
                  handleSend(prompt)
                }}
                disabled={loading}
                className="rounded-full border border-slate-800 bg-slate-900/80 px-3.5 py-1.5 text-xs text-cyan-300 hover:border-cyan-500/40 hover:bg-slate-800 transition disabled:opacity-50 text-left"
              >
                💡 {prompt}
              </button>
            ))}
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearHistory}
            disabled={loading}
            className="rounded-full border border-red-500/30 bg-red-950/40 px-4 py-1.5 text-xs text-red-400 hover:bg-red-900/50 transition disabled:opacity-50 shrink-0 self-end sm:self-auto"
          >
            🧹 Clear Chat
          </button>
        )}
      </div>

      {/* Main Chat Box Container */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 space-y-6 min-h-[480px] flex flex-col justify-between">
        {/* Chat Thread */}
        <div className="space-y-6 max-h-[550px] overflow-y-auto pr-2">
          {fetchingHistory ? (
            <div className="text-center py-10 text-xs text-slate-400">Loading conversation history...</div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
              <div className="h-14 w-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-3xl">
                🤖
              </div>
              <h3 className="text-lg font-semibold text-white">How can I help you today?</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Type any product question below or select one of the suggested prompts to start inquiring.
              </p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="space-y-3 animate-fadeIn">
                {/* User Message Bubble */}
                <div className="flex justify-end">
                  <div className="max-w-2xl rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-600 px-5 py-3.5 text-sm text-slate-950 font-medium shadow-md">
                    <p className="font-semibold text-slate-950">{msg.question}</p>
                  </div>
                </div>

                {/* AI Assistant Answer Bubble */}
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 text-sm font-bold">
                    🤖
                  </div>
                  <div className="max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/90 px-5 py-4 text-sm text-slate-200 shadow-lg space-y-2">
                    <div className="flex items-center justify-between text-[11px] text-cyan-400 font-semibold tracking-wide">
                      <span>E-COMMERCE ASSISTANT</span>
                    </div>
                    {msg.answer ? (
                      <MarkdownRenderer content={msg.answer} />
                    ) : (
                      <div className="flex items-center gap-2 text-xs text-cyan-400 py-1">
                        <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
                        Analyzing product vector index & generating response...
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="pt-4 border-t border-slate-800/80 space-y-3">
          <div className="relative">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              placeholder="Ask a question about products, specs, comparisons..."
              rows={2}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 p-4 pr-28 text-sm text-slate-100 placeholder-slate-500 outline-none resize-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="absolute right-3 bottom-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-5 py-2.5 text-xs font-semibold text-slate-950 transition hover:brightness-110 disabled:opacity-40 shadow-md"
            >
              {loading ? "Thinking..." : "Send Question 🚀"}
            </button>
          </div>
          <div className="flex justify-between items-center text-[11px] text-slate-400">
            <span>Press <kbd className="rounded bg-slate-800 px-1 py-0.5 font-mono">Enter</kbd> to send</span>
            <span className="text-cyan-400/80">{status}</span>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function ChatPage() {
  return (
    <main className="min-h-[calc(100vh-80px)] px-6 py-10">
      <Suspense fallback={<div className="text-center py-20 text-slate-400">Loading AI Assistant...</div>}>
        <ChatContent />
      </Suspense>
    </main>
  )
}
