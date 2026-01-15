import type { APIError } from '@/types/api'
import type { ChatRequest, ChatResponse } from '@/types/chat'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function apiClient<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('todo_jwt_token') : null

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    })

    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('todo_jwt_token')
        window.location.href = '/login'
      }
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: 'Request failed',
      }))
      const error: APIError = {
        message: errorData.error || 'Request failed',
        status: response.status,
      }
      throw error
    }

    if (response.status === 204) {
      return null as T
    }

    return (await response.json()) as T
  } catch (error) {
    if ((error as APIError).message) {
      throw error
    }
    throw {
      message: 'Network error, please try again',
      status: undefined,
    } as APIError
  }
}

/**
 * Send chat message to AI chatbot
 *
 * @param userId - User ID from authentication
 * @param request - Chat request with message and optional conversation_id
 * @returns ChatResponse with assistant message and tool calls
 */
export async function sendChatMessage(
  userId: string,
  request: ChatRequest
): Promise<ChatResponse> {
  return apiClient<ChatResponse>(`/api/${userId}/chat`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
