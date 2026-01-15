'use client'

import { ReactNode } from 'react'
import { Navbar } from './Navbar'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { getUserIdFromToken } from '@/lib/auth'

export function AppLayout({ children }: { children: ReactNode }) {
  const userId = getUserIdFromToken()

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      {userId && <ChatContainer userId={userId} />}
    </div>
  )
}
