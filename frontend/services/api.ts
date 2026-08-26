import axios from "axios"
import { Product, ChatMessage } from "@/types"

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
})

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export const getProducts = async (): Promise<Product[]> => {
  const response = await api.get<Product[]>("/products")
  return response.data
}

export const getProduct = async (id: string): Promise<Product> => {
  const response = await api.get<Product>(`/products/${id}`)
  return response.data
}

export const createProduct = async (product: Partial<Product>): Promise<Product> => {
  const response = await api.post<Product>("/products", product)
  return response.data
}

export const updateProduct = async (id: string, product: Partial<Product>): Promise<Product> => {
  const response = await api.put<Product>(`/products/${id}`, product)
  return response.data
}

export const deleteProduct = async (id: string): Promise<void> => {
  await api.delete(`/products/${id}`)
}

export const sendChatQuestion = async (question: string): Promise<ChatMessage> => {
  const response = await api.post<ChatMessage>("/chat", { question })
  return response.data
}

export const sendChatQuestionStream = async (
  question: string,
  onChunk: (chunk: string) => void
): Promise<void> => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api"
  const response = await fetch(`${baseUrl}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  })

  if (!response.ok || !response.body) {
    throw new Error(`Streaming failed with status ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder("utf-8")
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n\n")
    buffer = lines.pop() || ""

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const jsonStr = line.slice(6).trim()
        if (jsonStr) {
          try {
            const parsed = JSON.parse(jsonStr)
            if (parsed.text) {
              onChunk(parsed.text)
            }
          } catch (err) {
            console.error("Error parsing SSE JSON chunk", err)
          }
        }
      }
    }
  }

  if (buffer.trim().startsWith("data: ")) {
    const jsonStr = buffer.trim().slice(6).trim()
    if (jsonStr) {
      try {
        const parsed = JSON.parse(jsonStr)
        if (parsed.text) {
          onChunk(parsed.text)
        }
      } catch (err) {
        console.error("Error parsing final SSE JSON chunk", err)
      }
    }
  }
}

export const getChatHistory = async (): Promise<ChatMessage[]> => {
  const response = await api.get<ChatMessage[]>("/chat/history")
  return response.data
}

export const clearChatHistory = async (): Promise<void> => {
  await api.delete("/chat/history")
}

export default api


