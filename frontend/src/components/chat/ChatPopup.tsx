'use client'

import { useEffect, useRef, useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { useChat } from '@/hooks/useChat'

interface ChatPopupProps {
  userId: string
  onClose: () => void
}

export function ChatPopup({ userId, onClose }: ChatPopupProps) {
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { messages, isLoading, sendMessage } = useChat({
    userId,
    onError: (err) => {
      setError(err.message || 'Failed to send message')
      setTimeout(() => setError(null), 5000)
    },
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle Esc key to close chat
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  return (
    <div
      className="fixed bottom-0 right-0 z-50 flex h-[100dvh] w-full flex-col overflow-hidden bg-white shadow-2xl sm:bottom-6 sm:right-6 sm:h-[600px] sm:w-[400px] sm:rounded-lg"
      role="dialog"
      aria-label="AI Chat Assistant"
      aria-modal="true"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-blue-600 px-4 py-3 text-white">
        <h3 className="font-semibold" id="chat-title">AI Assistant</h3>
        <button
          onClick={onClose}
          className="rounded p-1 transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-white"
          aria-label="Close chat"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-gray-500">
            <div>
              <p className="text-lg font-medium">👋 Hello!</p>
              <p className="mt-2 text-sm">
                I can help you manage your tasks.
                <br />
                Try saying:
              </p>
              <ul className="mt-3 space-y-1 text-left text-sm">
                <li>• &quot;Add a task to buy groceries&quot;</li>
                <li>• &quot;Show me my tasks&quot;</li>
                <li>• &quot;Mark task as done&quot;</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        disabled={isLoading}
        placeholder="Type your message..."
      />
    </div>
  )
}
