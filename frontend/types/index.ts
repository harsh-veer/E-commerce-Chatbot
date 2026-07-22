export interface User {
  id: string
  first_name: string
  last_name: string
  email: string
  is_admin: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Product {
  id: string
  name: string
  brand: string
  category: string
  price: number
  discount: number
  description: string
  specifications: Record<string, string>
  rating: number
  stock: number
  images: string[]
}

export interface ChatMessage {
  id: string
  user_id: string
  question: string
  answer: string
  created_at: string
}
