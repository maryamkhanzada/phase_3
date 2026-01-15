'use client'

import { ChatMessage as ChatMessageType } from '@/types/chat'
import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-blue-600' : 'bg-gray-600'
        }`}
      >
        {isUser ? (
          <User className="h-5 w-5 text-white" />
        ) : (
          <Bot className="h-5 w-5 text-white" />
        )}
      </div>

      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="prose prose-sm max-w-none break-words text-sm">
          {isUser ? (
            <span className="whitespace-pre-wrap">{message.content}</span>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2 border-t border-gray-300 pt-2 text-xs opacity-70">
            {message.tool_calls.length} action
            {message.tool_calls.length > 1 ? 's' : ''} executed
          </div>
        )}
      </div>
    </div>
  )
}
