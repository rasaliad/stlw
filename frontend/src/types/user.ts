export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  is_active?: boolean
}

export interface UserUpdate {
  username?: string
  email?: string
  is_active?: boolean
}