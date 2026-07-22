"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import api from "@/services/api"
import FormInput from "@/components/FormInput"
import PageHeader from "@/components/PageHeader"

export default function SignupPage() {
  const router = useRouter()
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError("")

    try {
      await api.post("/auth/signup", { first_name: firstName, last_name: lastName, email, password })
      router.push("/auth/login")
    } catch (err) {
      setError("Unable to create account. Please try again.")
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <div className="mx-auto max-w-2xl rounded-3xl border border-slate-800 bg-slate-900/95 p-10 shadow-glow">
        <PageHeader title="Sign up" description="Create a new account and start asking product questions." />
        <form className="space-y-6" onSubmit={handleSubmit}>
          <FormInput id="firstName" label="First Name" value={firstName} onChange={setFirstName} />
          <FormInput id="lastName" label="Last Name" value={lastName} onChange={setLastName} />
          <FormInput id="email" label="Email" type="email" value={email} onChange={setEmail} />
          <FormInput id="password" label="Password" type="password" value={password} onChange={setPassword} />
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <button type="submit" className="w-full rounded-3xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
            Sign up
          </button>
        </form>
      </div>
    </main>
  )
}
