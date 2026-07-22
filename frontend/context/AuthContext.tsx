"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { AuthResponse, User } from "@/types"
import { setAuthToken } from "@/services/api"

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (data: AuthResponse, user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const storedToken = localStorage.getItem("ecom_token")
    const storedUser = localStorage.getItem("ecom_user")
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
      setAuthToken(storedToken)
    }
  }, [])

  const login = (data: AuthResponse, userData: User) => {
    localStorage.setItem("ecom_token", data.access_token)
    localStorage.setItem("ecom_user", JSON.stringify(userData))
    setUser(userData)
    setToken(data.access_token)
    setAuthToken(data.access_token)
  }

  const logout = () => {
    localStorage.removeItem("ecom_token")
    localStorage.removeItem("ecom_user")
    setUser(null)
    setToken(null)
  }

  return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
