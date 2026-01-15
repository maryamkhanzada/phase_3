'use client'

import { useState, useCallback } from 'react'
import { ChatMessage, ChatRequest } from '@/types/chat'
import { sendChatMessage } from '@/lib/api-client'

interface UseChatOptions {
  userId: string
  onError?: (error: Error) => void
}

interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  sendMessage: (content: string) => Promise<void>
  conversationId: string | null
}

export function useChat({ userId, onError }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return

      // Optimistic update: add user message immediately
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)

      try {
        const request: ChatRequest = {
          message: content.trim(),
          ...(conversationId && { conversation_id: conversationId }),
        }

        const response = await sendChatMessage(userId, request)

        // Update conversation ID if this is the first message
        if (!conversationId) {
          setConversationId(response.conversation_id)
        }

        // Add assistant response
        const assistantMessage: ChatMessage = {
          id: `${response.conversation_id}-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          tool_calls: response.tool_calls,
          timestamp: response.timestamp,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } catch (error) {
        // Remove optimistic user message on error
        setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id))

        const err = error instanceof Error ? error : new Error('Failed to send message')
        onError?.(err)
      } finally {
        setIsLoading(false)
      }
    },
    [userId, conversationId, isLoading, onError]
  )

  return {
    messages,
    isLoading,
    sendMessage,
    conversationId,
  }
}
