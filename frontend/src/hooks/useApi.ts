'use client'

import { apiClient } from '@/lib/api-client'
import type { APIError, LoadingState } from '@/types/api'
import { useCallback, useState } from 'react'

export function useApi<T = unknown>() {
  const [data, setData] = useState<T | null>(null)
  const [loadingState, setLoadingState] = useState<LoadingState>('idle')
  const [error, setError] = useState<APIError | null>(null)

  const execute = useCallback(async (endpoint: string, options?: RequestInit) => {
    setLoadingState('loading')
    setError(null)

    try {
      const result = await apiClient<T>(endpoint, options)
      setData(result)
      setLoadingState('success')
      return result
    } catch (err) {
      const apiError = err as APIError
      setError(apiError)
      setLoadingState('error')
      throw apiError
    }
  }, [])

  return {
    data,
    loadingState,
    error,
    execute,
    isLoading: loadingState === 'loading',
    isError: loadingState === 'error',
    isSuccess: loadingState === 'success',
  }
}
