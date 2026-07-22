"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "@/services/api"
import FormInput from "@/components/FormInput"
import PageHeader from "@/components/PageHeader"
import { useAuth } from "@/context/AuthContext"

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError("")

    try {
      const response = await api.post("/auth/login", { email, password })
      const token = response.data.access_token
      setAuthToken(token)
      login(response.data, response.data.user)
      router.push("/chat")
    } catch (err) {
      setError("Unable to login. Please check your credentials.")
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <div className="mx-auto max-w-2xl rounded-3xl border border-slate-800 bg-slate-900/95 p-10 shadow-glow">
        <PageHeader title="Login" description="Access your account and start asking product questions." />
        <form className="space-y-6" onSubmit={handleSubmit}>
          <FormInput id="email" label="Email" type="email" value={email} onChange={setEmail} />
          <FormInput id="password" label="Password" type="password" value={password} onChange={setPassword} />
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <button type="submit" className="w-full rounded-3xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
            Login
          </button>
        </form>
      </div>
    </main>
  )
}
