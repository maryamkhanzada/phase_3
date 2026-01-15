'use client'

import { MessageCircle } from 'lucide-react'

interface ChatIconProps {
  onClick: () => void
  unreadCount?: number
}

export function ChatIcon({ onClick, unreadCount = 0 }: ChatIconProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-50 rounded-full bg-blue-600 p-4 text-white shadow-lg transition-all hover:bg-blue-700 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label="Open chat"
    >
      <MessageCircle className="h-6 w-6" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-bold">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  )
}
