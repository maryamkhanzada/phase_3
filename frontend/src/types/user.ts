export interface User {
  id: string
  email: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface LoginFormData {
  email: string
  password: string
}

export interface SignupFormData {
  email: string
  password: string
}
