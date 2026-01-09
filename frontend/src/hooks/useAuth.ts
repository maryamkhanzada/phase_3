'use client'

import { apiClient } from '@/lib/api-client'
import { removeAuthToken, setAuthToken } from '@/lib/auth'
import type { AuthResponse, LoginFormData, SignupFormData, User } from '@/types/user'
import { useRouter } from 'next/navigation'
import { useCallback, useState } from 'react'

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(
    async (credentials: LoginFormData) => {
      setIsLoading(true)
      setError(null)

      try {
        const data = await apiClient<AuthResponse>('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify(credentials),
        })

        setAuthToken(data.token)
        setUser(data.user)
        router.push('/app/tasks')
      } catch (err) {
        setError((err as { message: string }).message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [router]
  )

  const signup = useCallback(
    async (credentials: SignupFormData) => {
      setIsLoading(true)
      setError(null)

      try {
        const data = await apiClient<AuthResponse>('/api/auth/signup', {
          method: 'POST',
          body: JSON.stringify(credentials),
        })

        setAuthToken(data.token)
        setUser(data.user)
        router.push('/app/tasks')
      } catch (err) {
        setError((err as { message: string }).message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [router]
  )

  const logout = useCallback(() => {
    removeAuthToken()
    setUser(null)
    router.push('/login')
  }, [router])

  return {
    user,
    isLoading,
    error,
    login,
    signup,
    logout,
  }
}
