export const AUTH_TOKEN_KEY = 'todo_jwt_token'

export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_TOKEN_KEY, token)
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_TOKEN_KEY)
  }
  return null
}

export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_TOKEN_KEY)
  }
}

export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}

export function getUserIdFromToken(): string | null {
  const token = getAuthToken()
  if (!token) return null

  try {
    // Decode JWT payload (second part of token)
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.user_id || null
  } catch {
    return null
  }
}
